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

    def State(self):
        state = np.asarray([len(self.inputPlace)])
        return state
    
    def Capacity(self):
        return 1 

    def __str__(self):
        return f'sink:{self.name}, {len(self.inputPlace)}'
     