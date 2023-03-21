import numpy as np

from transition import Transition
from place import Place
from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY

IDLE = 0
WORKING = 1
WAITING = -1 

#      return to
#      conveyor    ┌┐             ┌┐              ┌┐
#          .─.     ││     .─.     ││      .─.     ││
#     ───▶(   )───▶││───▶(   )───▶││...─▶(   )───▶││
#          `─'     ││     `─'     ││      `─'     ││
#           ▲      └┘      ▲      └┘      ▲       └┘
#           └──────────┐   │   ┌───....───┘
#                     ┌┴───┴───┴┐ output transition 
#                     └────▲────┘     
#                         .┴.
#                        (   )
#                         `▲'
#                     ┌────┴────┐input transition
#                     └─▲──▲──▲─┘      
#           ┌───────────┘  │  └────....────┐
#           │      ┌┐      │      ┌┐       │      ┌┐
#          .─.     ││     .─.     ││      .─.     ││
#     ───▶(   )───▶││───▶(   )───▶││...─▶(   )───▶││
#          `─'     ││     `─'     ││      `─'     ││
#                  └┘             └┘              └┘
#    source
#   conveyor
class Agent:
    def __init__(self, name, delayFn, actionFn, predicateFn = lambda p: True, isSerial = False, maximumWaitTime = -1):
        self.name = name
        self.inputDelayFn = lambda : 0 
        self.outputDelayFn = delayFn
        self.actionFn = actionFn
        self.predicateFn = predicateFn
        self.isSerial = isSerial
        self.currentStatus = IDLE 
        self.waitTime = 0
        self.maximumWaitTime = maximumWaitTime
        self.make()


    def make(self): 
        def inputAgentTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if phase == PHASE_SECONDARY:
                return BLOCKED

            outputPlace = outputPlaces[0]

            if outputPlace.IsFull() :
                return BLOCKED
            
            for ix in range(len(inputPlaces)-1, -1, -1):
                p = inputPlaces[ix]
                if not p.IsEmpty() and not p.IsDisabled():
                    v = p[0]
                    if self.predicateFn(v):
                        self.currentStatus = WORKING 
                        v = p.Remove()
                        outputPlace.Add(v)
                        if self.isSerial:
                            p.Disable() 
                    return FINISHED
                
            return BLOCKED

        def outputAgentTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if phase == PHASE_SECONDARY:
                return BLOCKED

            inputPlace = inputPlaces[0] 

            for p in outputPlaces:
                if self.isSerial:
                       p.Enable() 
                if not p.IsFull() and not p.IsDisabled():
                    v = inputPlace.Remove()
                    self.actionFn(v)
                    p.Add(v)
                    self.currentStatus = IDLE
                    return FINISHED
                
            self.currentStatus = WAITING
            self.waitTime += 1  
            if self.maximumWaitTime > 0 and self.waitTime > self.maximumWaitTime:
                raise Exception(f'Agent:{self.name} exceeded maximum wait time of {self.maximumWaitTime}')
            return BLOCKED
        
        self.inputTransition = Transition(self.inputDelayFn, inputAgentTransitionFn)
        self.outputTransition = Transition(self.outputDelayFn, outputAgentTransitionFn)
        self.place = Place(capacity=1)

    def Connect(self, sourceConveyor, returnToConveyor):
        if self.isSerial and (sourceConveyor != returnToConveyor):
            raise Exception("Serial agents cannot connect to different conveyors")
        
        for p in sourceConveyor.Places():
            self.inputTransition.AddInputPlace(p)
        
        self.inputTransition.AddOutputPlace(self.place) 
        self.outputTransition.AddInputPlace(self.place)

        for p in returnToConveyor.Places():
            self.outputTransition.AddOutputPlace(p)

    def ScheduleTransitions(self, scheduler, t):
        if self.inputTransition.IsEnabled():
            self.inputTransition.ScheduleExecute(scheduler, t)

        if self.outputTransition.IsEnabled():
            self.outputTransition.ScheduleExecute(scheduler, t)

    def State(self):
        state = np.asarray([0 if self.place.IsEmpty() else 1])
        return state
    
    def DeepState(self):
        state = np.asarray([0 if self.place.IsEmpty() else self.place[0].Id()])
        return state
    
    def Capacity(self):
        return 1

    def Reset(self):
        self.waitTime = 0
        self.currentStatus = IDLE 
        if len(self.place) > 0:
            self.place.Remove()
        
    def Transitions(self):
        return [self.inputTransition, self.outputTransition]
    
    def __str__(self):
        s = f'{self.name}:'
        s += f' {self.place}'
        return s
 
if __name__ == "__main__":
    import numpy as np
    from conveyor import Conveyor
    from simulator import Simulator
    from box import Box
    from sink import Sink
    from source import Source, SKIP, FIFO 
    
    def test1():
        simulator = Simulator()

        class simpleSource:
            def __init__(self):
                self.last_t = -1
                self.last_value = -1 
                self.burst_size = 5
                self.wait_time = 50
                self.state = 0 
                self.ctr = 0 

            def __call__(self, currentTime):
                if currentTime != self.last_t:
                    self.last_t = currentTime               
                    if self.state == 0:
                        if self.ctr < self.burst_size:
                            self.ctr += 1
                            self.last_value = FIFO
                            print(f'currentTime = {currentTime}, ctr = {self.ctr}, FIFO')
                        else:
                            self.state = 1
                            self.ctr = 0 
                            self.last_value = SKIP
                            print(f'currentTime = {currentTime}, ctr = {self.ctr}, SKIP - start')
                    elif self.state == 1:
                        if self.ctr < self.wait_time:
                            self.ctr += 1
                            self.last_value = SKIP
                            print(f'currentTime = {currentTime}, ctr = {self.ctr}, SKIP')
                        else:
                            self.state = 0
                            self.ctr = 0 
                            self.last_value = FIFO
                            print(f'currentTime = {currentTime}, ctr = {self.ctr}, FIFO - start')
                return self.last_value
            
        items = []
        for i in range(10):
            items.append(Box(i, 3))

        agent = Agent("agent", lambda: 20, lambda v: v.Pick(1), maximumWaitTime=10)
        source = Source('SOURCE', items, simpleSource())
        c1 = Conveyor('C1', 10, 0)
        s01 = Conveyor('S01', 5, 0)
        sink = Sink('SINK')

        source.Connect(c1.FirstPlace())
        agent.Connect(c1, s01)

        components = [source, c1, s01, agent, sink]

        for t in range(400):
            try:
                simulator.Step(t, components)
                states = [np.sum(c.State())/c.Capacity() for c in components]
                print(states)
                print(t, c1, s01, agent, sink)

                if states[-1] == len(items):
                    print('finished')
                    break 
            except Exception as e:
                print(f'error at t = {t} {e}')
                break 
    def test2():
        simulator = Simulator()

        class simpleSource:
            def __init__(self):
                self.last_t = -1
                self.last_value = -1 
                self.burst_size = 10
                self.wait_time = 10
                self.state = 0 
                self.ctr = 0 

            def __call__(self, currentTime):
                if currentTime != self.last_t:
                    self.last_t = currentTime               
                    if self.state == 0:
                        if self.ctr < self.burst_size:
                            self.ctr += 1
                            self.last_value = FIFO
                        else:
                            self.state = 1
                            self.ctr = 0 
                            self.last_value = SKIP
                    elif self.state == 1:
                        if self.ctr < self.wait_time:
                            self.ctr += 1
                            self.last_value = SKIP
                        else:
                            self.state = 0
                            self.ctr = 0 
                            self.last_value = FIFO
                return self.last_value
            
        items = []
        for i in range(100):
            items.append(Box(i+1, 3))

        agent = Agent("agent", 
                    delayFn = lambda: 5, 
                    actionFn = lambda v: v.Pick(1), 
                    predicateFn= lambda v: v.IsForStation(1),
                    isSerial=True)
        
        source = Source('SOURCE', items, simpleSource())
        c0 = Conveyor('C0', 10, 0)
        c1 = Conveyor('C1', 1, 0, exitPredicateFn=lambda p: not p.IsForStation(1))
        c2 = Conveyor('c2', 5, 0)
        sink = Sink('SINK')

        source.Connect(c0.FirstPlace())
        c0.Connect(c1.FirstPlace())
        c1.Connect(c2.FirstPlace())
        c2.Connect(sink.FirstPlace())
        agent.Connect(c1, c1)

        components = [source, c0, c1, agent, c2, sink]
        
        allStates = np.zeros(17)
        for t in range(400):
            try:
                simulator.Step(t, components)
                #states = [np.sum(c.State())/c.Capacity() for c in components]
                states = components[1].DeepState()
                for c in components[2:-1]:
                    states = np.hstack((states, c.DeepState()))
                print(states)
                allStates = np.vstack((allStates, states))
            
                if components[-1].State() == len(items):
                    print('finished')
                    break 
            except Exception as e:
                print(f'exception at t = {t} {e}')
                break 
        np.save('data/states.npy', allStates)
    
    #test2()
    test1()