import numpy as np
import random

from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY
from place import Place
from transition import Transition

class Merger:
    def __init__(self, name, capacity = 2, delay=0):
        self.name = name   
        self.capacity = capacity     
        self.delayFn = lambda: delay
        self.enabled = True
        self.make()

    def make(self):
        def mergerTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if len(outputPlaces) == 0:
                return FINISHED

            if self.IsStopped():
                return FINISHED

            outputPlace = outputPlaces[0]

            inputPlace = inputPlaces[0]

            if not outputPlace.IsFull() :
                if not inputPlace.IsEmpty():
                    v = inputPlace.Remove()
                    outputPlace.Add(v)
                return FINISHED
            else:
                return BLOCKED

        self.transition = Transition(self.delayFn, mergerTransitionFn)
        self.inputPlace = Place(capacity=self.capacity)
        self.transition.AddInputPlace(self.inputPlace)

    def Connect(self, nextPlace):
        _, countOutputPlaces = self.transition.CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The merger {self.name} is already connected")
        
        self.transition.AddOutputPlace(nextPlace) 

    def ScheduleTransitions(self, scheduler, t):
        if self.transition.IsEnabled():
            self.transition.ScheduleExecute(scheduler, t)

    def State(self):
        state = np.asarray([len(self.inputPlace)])
        return state
    
    def DeepState(self):
        raise NotImplementedError
    
    def Capacity(self):
        return self.capacity
    
    def FirstPlace(self):
        return self.inputPlace
    
    def Stop(self):
        self.enabled = False
        self.inputPlace.Disable()

    def Start(self):
        self.enabled = True
        self.inputPlace.Enable()
 
    def IsStopped(self):
        return self.enabled == False
    
    def Reset(self):
        self.inputPlace.Remove()
        self.Start()

    def Transitions(self):
        return [self.transition]
    
    def __str__(self):
        s = f'{self.name}:'
        s += f' {self.inputPlace}'
        return s
        
if __name__ == "__main__":
    from simulator import Simulator
    from source import Source, FIFO, SKIP
    from conveyor import Conveyor
    from sink import Sink
    from box import Box

    class timedSource:
        def __init__(self, even):
            self.last_t = -1
            self.last_value = -1
            self.even = even

        def __call__(self, currentTime):
            if currentTime != self.last_t:
                self.last_t = currentTime 
            
                if self.even and currentTime % 2 == 0:
                    self.last_value = FIFO
                elif not self.even and currentTime % 2 != 0:
                    self.last_value = FIFO
                else:
                    self.last_value = SKIP

            return self.last_value

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
    
    simulator = Simulator()

    items_even = []
    items_odd  = []
    items_all  = []
    for i in range(1):
        items_even.append(Box(f'E{i}', 3))
        items_odd.append(Box(f'O{i}', 3))
        items_all.append(Box(f'A{i}', 3))
        

    evenSource = Source(name ='EvenSource', values = items_even, sourceFn = timedSource(True))
    oddSource = Source(name = 'OddSource', values = items_odd, sourceFn = timedSource(False))
    allSource = Source(name = 'AllSource', values = items_all, sourceFn = simpleSource())
    sink = Sink(name = 'SINK')

    c1 = Conveyor(name = 'C1', capacity = 10, delay = 0)

    cs1 = Conveyor(name = 'Cs1', capacity = 3, delay = 0)
    cs2 = Conveyor(name = 'Cs2', capacity = 3, delay = 0)
    cs3 = Conveyor(name = 'Cs3', capacity = 3, delay = 0)

    merger = Merger(name = 'M1', capacity=3, delay = 0)
    
    evenSource.Connect(cs1.FirstPlace())
    oddSource.Connect(cs2.FirstPlace())
    allSource.Connect(cs3.FirstPlace())

    cs1.Connect(merger.FirstPlace())
    cs2.Connect(merger.FirstPlace())
    cs3.Connect(merger.FirstPlace())

    merger.Connect(c1.FirstPlace())
    c1.Connect(sink.FirstPlace())

    components = [evenSource, oddSource, allSource, cs1, cs2, cs3, merger, c1, sink]

    for t in range(60):
        ok, iterations, e, = simulator.Step(t, components)
        states = [np.sum(c.State())/c.Capacity() for c in components]
        #print(states)
        if not ok:
            print(e)
            break
        for c in [cs1, cs2, cs3, merger, c1, sink]:
            print(c)

        if states[-1] == (len(items_even) + len(items_odd) + len(items_all)):
            print('finished')
            break 
