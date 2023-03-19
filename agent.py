from transition import Transition
from place import Place

INACTIVE = 0 
ACTIVE = 1
BLOCKED = -1 

class Agent:
    def __init__(self, name, delayFn):
        self.name = name
        self.agentState = INACTIVE
        self.inputDelayFn = lambda : 0 
        self.outputDelayFn = delayFn
        self.make()


    def make(self): 
        def inputAgentTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            pass
        def outputAgentTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            pass

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



