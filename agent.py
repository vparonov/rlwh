from transition import Transition
from place import Place
from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY

#            input         output          
#          transition    transition        
#              ┌┐     .     ┌┐ *actionFn             
#          ───▶││───▶( )───▶││───▶         
#    source    └┘     '     └┘  return to  
#   conveyor                    conveyor  

class Agent:
    def __init__(self, name, delayFn, actionFn):
        self.name = name
        self.inputDelayFn = lambda : 0 
        self.outputDelayFn = delayFn
        self.actionFn = actionFn
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
                if not p.IsEmpty():
                    v = p.Remove()
                    outputPlace.Add(v)
                    return FINISHED
                
            return BLOCKED

        def outputAgentTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if phase == PHASE_SECONDARY:
                return BLOCKED

            inputPlace = inputPlaces[0] 

            for p in outputPlaces:
                if not p.IsFull():
                    v = inputPlace.Remove()
                    self.actionFn(v)
                    p.Add(v)
                    return FINISHED
                
            return BLOCKED
        
        self.inputTransition = Transition(self.inputDelayFn, inputAgentTransitionFn)
        self.outputTransition = Transition(self.outputDelayFn, outputAgentTransitionFn)
        self.place = Place(capacity=1)

    def Connect(self, sourceConveyor, returnToConveyor):
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
        state = np.asarray([self.place.IsEmpty()])
        return state

    def Capacity(self):
        return 1

    def Reset(self):
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
   
    simulator = Simulator()

    class simpleSource:
        def __init__(self):
            self.last_t = -1
            self.last_value = -1 

        def __call__(self, currentTime):
            if currentTime != self.last_t:
                self.last_t = currentTime           
                if currentTime % 1 == 0:
                    self.last_value = FIFO
                else:
                    self.last_value = SKIP

            return self.last_value
        
    items = []
    for i in range(10):
        items.append(Box(i, 3))

    agent = Agent("agent", lambda: 9, lambda v: v.Pick(1))
    source = Source('SOURCE', items, simpleSource())
    c1 = Conveyor('C1', 10, 0)
    s01 = Conveyor('S01', 5, 0)
    sink = Sink('SINK')

    source.Connect(c1.FirstPlace())
    s01.Connect(sink.FirstPlace())
    agent.Connect(c1, s01)

    components = [source, c1, s01, agent, sink]

    for t in range(200):
        ok, iterations, e, = simulator.Step(t, components)
        states = [np.sum(c.State())/c.Capacity() for c in components]
        print(states)

        if not ok:
            print(e)
            break
 
        print(t, c1, s01, agent, sink)

        if states[-1] == len(items):
            print('finished')
            break 
