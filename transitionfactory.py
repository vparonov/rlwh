from transition import Transition

class TransitionFactory:
    def __init__(self, placeRegistry, scheduler):
        self.placeRegistry = placeRegistry
        self.scheduler = scheduler
        self.transitions = []

    def MakeTransition(self, delayFn, actionFn):
        transition = Transition(self.placeRegistry, self.scheduler, delayFn, actionFn)
        self.transitions.append(transition)
        return transition
    
    def GetTransitions(self):
        return self.transitions
