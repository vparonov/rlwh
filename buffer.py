import numpy as np

from place import Place
from transition import Transition
from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY

class Buffer:
    def __init__(self, name, capacity) -> None:
        self.capacity = capacity
        self.delayFn = lambda: 0
        self.name = name

        self.make()

    def make(self) -> None:
        def bufferTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
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
    
        self.transition = Transition(self.delayFn, bufferTransitionFn)
        self.inputPlace = Place(capacity=self.capacity)
        self.transition.AddInputPlace(self.inputPlace)

    def Connect(self, nextPlace):
        _, countOutputPlaces = self.transition.CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The buffer {self.name} is already connected")
        
        self.transition.AddOutputPlace(nextPlace) 

    def ScheduleTransitions(self, scheduler, t):
        if self.transition.IsEnabled():
            self.transition.ScheduleExecute(scheduler, t)

    def State(self):
        return len(self.inputPlace) / self.capacity
    
    def DeepState(self):
        state = np.zeros(self.inputPlace.capacity)
        ix = 0 
        for b in self.inputPlace:
            state[ix] = b.Id()
            ix += 1
        return state 
    
    def Capacity(self):
        return self.capacity
    
    def FirstPlace(self):
        return self.inputPlace
    
    def Reset(self):
        self.inputPlace.Clear()
        self.transition.Reset()

    def Transitions(self):
        return [self.transition]
    
    def __str__(self):
        s = f'{self.name}:'
        s += f' {self.inputPlace}'
        return s
        