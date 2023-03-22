import json
import glob
import random
import traceback 
import numpy as np

from conveyor import Conveyor
from diverter import Diverter, DIVERT, CONTINUE_STRAIGHT
from agent import Agent, BLOCKED
from sink import Sink
from source import Source, FIFO, SKIP
from box import BoxListFromFile
from simulator import Simulator

PRINT_STACK_TRACE = False  

class Warehouse:
    def __init__(self, name, fileName, datadir, randomFileSelect = False):
        self.name = name
        self.randomFileSelect = randomFileSelect
        if datadir != None:
            self.datafiles = self.enumerateDataFiles(datadir)
            random.shuffle(self.datafiles)
            self.fileIx = 0
        else:
            self.datafiles = []
        
        self.action_space = ActionSpace([SKIP, FIFO])
        self.simulator = Simulator()
        self.build(fileName)
        
    def build(self, fileName):
        with open(fileName) as f:
            data = json.load(f)
        components = {} 
        
        self.strategy = ActionStrategy()

        components['source'] =  (Source(name='source', values = [], sourceFn = self.strategy), 'source', -1)
        components['sink'] = (Sink('sink'), 'sink', 999999999)
        
        self.stateSize = 2 

        for c in data['components']:
            type = c['type']
            name = c['name']
            ord = c['ord']
            if name == 'source' or name == 'sink':
                raise Exception('source and sink are reserved names')
            
            if type == 'conveyor':
                capacity = c['capacity'] 
                newComponent = Conveyor(name = name, 
                                        capacity = capacity, 
                                        delay = c['delay'])
                self.stateSize += capacity
            elif type == 'diverter':
                newComponent = Diverter(name = name, 
                                        delay = c['delay'], 
                                        selectorFn = makeDiverterSelectorFn(c['divertStation']))
                self.stateSize += 1
            elif type == 'agent':
                newComponent = Agent(name = name, 
                                    delayFn = makeAgentDelayFn(c['minDelay'], c['maxDelay']), 
                                    actionFn= makeAgentMarkPickedFn(c['markPicked']), 
                                    maximumWaitTime=c['maxWaitingTime'])
                self.stateSize += 1
            else:
                print('Unknown component type:'+ type)

            components[c['name']] = (newComponent, type, ord)

        for conn in data['connections']:
            component, type, _ = components[conn['from']]
            if type == 'conveyor':
                to, _, _ = components[conn['to']]
                component.Connect(to.FirstPlace())
            elif type == 'diverter':
                to, _, _ = components[conn['to']]
                divertTo, _, _ = components[conn['divertTo']]
                component.Connect(to.FirstPlace(), divertTo.FirstPlace())
            elif type == 'agent':
                source, _, _  = components[conn['source']]
                returnTo, _, _ = components[conn['returnTo']]
                component.Connect(source, returnTo)
            elif type == 'source':
                to, _, _ = components[conn['to']]
                component.Connect(to.FirstPlace())
            else:
                print('Connections. Unknown component type:'+ type)

        self.componentsList = [c[1][0] for c in sorted(components.items(), key=lambda cc: cc[1][-1])]

        self.components = components
    
    def getAgentsWaitingRatio(self):
        ttl = 0 
        ttl_blocked = 0 
        for c in self.componentsList:
            if type(c).__name__ == 'Agent':
                currentStatus = c.GetCurrentStatus()
                ttl +=1 
                if currentStatus == BLOCKED:
                    ttl_blocked += 1
        if ttl > 0:
            return float(ttl_blocked)/float(ttl)
        else:
            return 0 

    def reward(self, state, terminated, truncated):
        #return self.reward_min_processing_time(state, terminated, truncated)
        return self.reward_min_total_time(state, terminated, truncated)
    
    def reward_min_total_time(self, state, terminated, truncated):
        if terminated:
            avgTotalProcessingTime =  self.t / self.components['sink'][0].State()[0]
            if avgTotalProcessingTime > 0:
                return 5.0/avgTotalProcessingTime
            else:
                return 0.0
        elif truncated:
            return 0.0
        elif self.t > 0:
            return -0.04 * self.getAgentsWaitingRatio()
        else:
            return 0.0
        
    def reset(self,itemsToPick = None):

        if itemsToPick == None:
            fileName = self.sampleDataFiles()
            print(fileName)
            itemsToPick = BoxListFromFile(fileName)
            if random.random() > 0.8:
                sort = random.randint(0, 2)
                if sort == 0 :
                    itemsToPick.sort(reverse=False, key=lambda b: b.route)
                elif sort == 1: 
                    itemsToPick.sort(reverse=True, key=lambda b: 1 if b.route == 2 else 0 )
                else:
                    itemsToPick.sort(reverse=True, key=lambda b: b.route)

        self.componentsList[0].Reset(itemsToPick)
        for c in self.componentsList[1:]:
            c.Reset()

        for item in itemsToPick:
            item.Reset()
        
        self.simulator.Reset()

        state = self.getState() 
        self.t = 0
        self.maxT = 5000#self.calcMaxT(itemsToPick)
        self.nitems= len(itemsToPick)
        return state, self.nitems, self.strategy.getActionsMask() 

    def step(self, action):
        self.strategy.setAction(action)
        terminated = False 
        truncated = False 
        info = ''
        actionsMask = self.strategy.getEmptyActionsMask()
        avgPickTime = -1 
        try:
            #print(self.t, action)
            if self.t > self.maxT:
                raise Exception(f'the maximum simulation time of {self.maxT} steps reached')
            
            #Step returns the number of iterations. it's not important, but it's useful for debugging
            _ = self.simulator.Step(self.t, self.componentsList)

            actionsMask = self.strategy.getActionsMask() 
            state = self.getState() 
            reward = self.reward(state, False, False)
            avgPickTime = 0# TODO self.components['sink'].avgPickTime()
        
            if self.components['sink'][0].CountReceived() == self.nitems:
                terminated = True
                reward = self.reward(state, True, False)
        except Exception as e:
            if PRINT_STACK_TRACE:
                stack_trace = traceback.format_exc()
                print(stack_trace)
            info = e
            state = self.getState()
            reward = self.reward(state, False, True)
            truncated = True 
        self.t += 1 
        return state, reward, terminated, truncated, (info, int(state[0]), actionsMask, avgPickTime)
 
    def getState(self):
        states = np.sum(self.componentsList[0].State()) / self.componentsList[0].Capacity()
        for c in self.componentsList[1:]:
            states = np.hstack((states, np.sum(c.State()) / c.Capacity()))
        return states.astype('float32')

    def enumerateDataFiles(self, dataDir):
        return glob.glob(f'{dataDir}/*.txt')

    def sampleDataFiles(self):
        if self.randomFileSelect:
            return random.sample(self.datafiles, k=1)[0]
        else:
            f = self.datafiles[self.fileIx]
            self.fileIx = (self.fileIx + 1) % len(self.datafiles)
            return f

# helper classes 
class ActionSpace():
    def __init__(self, actions):
        self.actions = actions 
        self.n = len(self.actions)
    
    def sample(self):
        return random.sample(self.actions, k=1)[0]
    
class ActionStrategy:
    def __init__(self):
        self.ix = 0 
        self.remaining_items = 0
  
    # def setItems(self, items):
    #     self.ix = 0 
    #     self.items= items
    #     self.remaining_items = len(self.items)

    def setAction(self, action):
        self.action = action 

    def getActionsMask(self):    
        # no masked actions 
        return [True, True]

    def getEmptyActionsMask(self):
        return [False, False]

    def __call__(self, ctime):
        return self.action 

# helper functions
def makeDiverterSelectorFn(station):
    def fn(box):
        return DIVERT if box.IsForStation(station) else CONTINUE_STRAIGHT
    return fn

def makeAgentDelayFn(fromDelay, toDelay):
    def fn():
        return random.randint(fromDelay, toDelay)
    return fn

def makeAgentMarkPickedFn(station):
    def fn(box):
        return box.Pick(station)
    return fn



if __name__ == '__main__':
    from box import Box 

    items = []
    for i in range(100):
        items.append(Box(i+1, 's', 3))

    wh = Warehouse('test', 'configurations/wh.json', None, False)
    state, nitems, mask  = wh.reset(items)
    print(state, nitems, mask)

    state, reward, terminated, truncated, (info, nitems, actionsMask, avgPickTime) = wh.step(FIFO)
    print(state, reward, terminated, truncated)
 
