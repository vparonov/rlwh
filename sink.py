import numpy as np 

from place import Place

class Sink:
    def __init__(self, name):
        self.name = name
        self.inputPlace = Place(capacity=-1)

    def Reset(self):
        self.inputPlace.Clear()

    def FirstPlace(self):
        return self.inputPlace
    
    def ScheduleTransitions(self, scheduler, t):
        pass 

    def SetCapacity(self, capacity):
        self.inputPlace.capacity = capacity

    def Count(self):
        return len(self.inputPlace)
    
    def State(self):
        return len(self.inputPlace) / self.inputPlace.capacity
    
    def DeepState(self):
        state = np.zeros(self.inputPlace.capacity)
        ix = 0 
        for b in self.inputPlace:
            state[ix] = b.Id()
            ix += 1
        return state 
    
    def CountReceived(self):
        return len(self.inputPlace)
    
    def Capacity(self):
        return 1 

    def __str__(self):
        return f'sink:{self.name}, {len(self.inputPlace)}'
     