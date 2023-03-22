import numpy as np

from scheduler import BLOCKED, FINISHED, PHASE_SECONDARY
from place import Place
from transition import Transition

CONTINUE_STRAIGHT = 0
DIVERT = 1

FORWARD=0
BACKWARD=1

class Diverter:
    def __init__(self, name, delay=0, type = BACKWARD, selectorFn = lambda box: CONTINUE_STRAIGHT):
        self.name = name        
        self.delayFn = lambda: delay
        self.enabled = True
        self.selectorFn = selectorFn
        self.type = type
        self.make()

    def make(self):
        def diverterTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if len(outputPlaces) == 0:
                return FINISHED

            if self.IsStopped():
                return FINISHED

            inputPlace = inputPlaces[0]
            
            if inputPlace.IsEmpty():
                return FINISHED
            
            action = self.selectorFn(self.inputPlace[0])
            
            # the forward diverter falls back to strait direction if it can't divert the box
            # the backward diverter blocks till divertion is complete 
            if phase == PHASE_SECONDARY and self.type == FORWARD:
                action = CONTINUE_STRAIGHT

            if action == CONTINUE_STRAIGHT:
                outputPlace = outputPlaces[0]
            elif action == DIVERT:
                outputPlace = outputPlaces[1]
            else:
                raise Exception("Diverter: Unknown action: " + str(action))
            
            if not outputPlace.IsFull() :
                v = inputPlace.Remove()
                outputPlace.Add(v)
                return FINISHED
            else:
                return BLOCKED

        self.inputPlace = Place(capacity=1)
        self.transition = Transition(self.delayFn, diverterTransitionFn)
        self.transition.AddInputPlace(self.inputPlace)

    def Connect(self, nextPlaceStraight, nextPlaceDivert):
        _, countOutputPlaces = self.transition.CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The diverter {self.name} is already connected")
        
        self.transition.AddOutputPlace(nextPlaceStraight) 
        self.transition.AddOutputPlace(nextPlaceDivert) 

    def ScheduleTransitions(self, scheduler, t):
        if self.transition.IsEnabled():
            self.transition.ScheduleExecute(scheduler, t)

    def State(self):
        state = np.asarray([1 if not self.inputPlace.IsEmpty() else 0 ])
        return state

    def DeepState(self):
        state = np.asarray([0 if self.inputPlace.IsEmpty() else self.inputPlace[0].Id()])
        return state
   
    def Capacity(self):
        return 1
    
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
        if len(self.inputPlace) > 0:
            self.inputPlace.Remove()
        self.transition.Reset()
        self.Start()

    def Transitions(self):
        return [self.transition] 
    
    def __str__(self):
        s = f'{self.name}:{self.inputPlace}'
        return s