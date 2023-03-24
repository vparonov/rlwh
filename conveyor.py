import numpy as np

from place import Place
from transition import Transition
from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY

BEGINNING = 0
END = 1
ANYWHERE = -1

class Conveyor:
    def __init__(self, name, capacity, delay=0, exitPredicateFn = lambda p: True):
        self.capacity = capacity
        self.delayFn = lambda: delay
        self.exitPredicateFn = exitPredicateFn
        self.name = name
        self.enabled = True
        self.places = []
        self.transitions = []

        self.make()

    def make(self):
        def conveyorTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if phase == PHASE_SECONDARY:
                return BLOCKED
            
            if len(outputPlaces) == 0:
                return FINISHED
            
            if self.IsStopped():
                return FINISHED
            
            outputPlace = outputPlaces[0]

            if outputPlace.IsDisabled():
                return FINISHED
            
            inputPlace = inputPlaces[0]
            
            if not outputPlace.IsFull() :
                if not inputPlace.IsEmpty():
                    v = inputPlace.Remove()
                    outputPlace.Add(v)
                return FINISHED
            else:
                return BLOCKED

        def lastTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            # the last transition is not moving the item to the output place
            # if the exitPredicateFn returns false
            # this is used to model the A-Frame behavior
            inputPlace = inputPlaces[0]
            if not inputPlace.IsEmpty(): 
                v = inputPlace[0]
                if not self.exitPredicateFn(v):
                    return FINISHED
                
            return conveyorTransitionFn(inputPlaces, outputPlaces, currentTime, phase)

        prevTransition = None
        for _ in range(self.capacity):
            newPlace  = Place(capacity=1)
            newTransition = Transition(self.delayFn, conveyorTransitionFn)
            self.places.append(newPlace)
            self.transitions.append(newTransition)

            newTransition.AddInputPlace(newPlace)
            if prevTransition is not None:
                prevTransition.AddOutputPlace(newPlace)

            prevTransition = newTransition
        #the last transition has augmented transition action 
        self.transitions[-1].SetActionFn(lastTransitionFn)

    def Connect(self, nextPlace):
        _, countOutputPlaces = self.transitions[-1].CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The conveyor {self.name} is already connected")
        
        self.transitions[-1].AddOutputPlace(nextPlace) 

    def ScheduleTransitions(self, scheduler, t):
        for i in range(len(self.transitions)-1, -1, -1):
            if self.transitions[i].IsEnabled():
                self.transitions[i].ScheduleExecute(scheduler, t)

    def State(self):
        cntFull = 0.0
        for p in self.places:
            if p.IsFull():
                cntFull += 1
        return cntFull / self.capacity
    
    def DeepState(self):
        state = np.asarray([0 if p.IsEmpty() else p[0].Id()  for p in self.places])
        return state
    
    def Capacity(self):
        return self.capacity
    
    def FirstPlace(self):
        return self.places[0]
    
    def Places(self):
        return self.places
    
    def Stop(self):
        self.enabled = False
        self.places[0].Disable()

    def Start(self):
        self.enabled = True
        self.places[0].Enable()
 
    def IsStopped(self):
        return self.enabled == False
    
    def Reset(self):
        for place in self.places:
            if len(place) > 0:
                place.Remove()
                
        for transition in self.transitions:
            transition.Reset()
        self.Start()

    def Transitions(self):
        return self.transitions

    def __str__(self):
        s = f'{self.name}:'
        for place in self.places:
            s += f' {place}'
        return s

if __name__ == "__main__":
    from scheduler import Scheduler

    scheduler = Scheduler()

    c = Conveyor("c1", 10, 0)

    c2 = Conveyor("c2", 10, 0)

    c.Connect(c2.FirstPlace())

    c2.Stop()
    c.PutValue('A')
    print(c)

    for t in range(25):
       
        if t == 22:
            c2.Start()
        scheduler.Execute(t)    
        c.ScheduleTransitions(scheduler, t)
        c2.ScheduleTransitions(scheduler, t)
        scheduler.Execute(t) 
        print(t, c, c2) 

