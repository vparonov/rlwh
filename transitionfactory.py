from transition import Transition

class TransitionFactory:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.transitions = []

    def MakeTransition(self, delayFn, actionFn):
        transition = Transition(self.scheduler, delayFn, actionFn)
        self.transitions.append(transition)
        return transition
    
    def GetTransitions(self):
        return self.transitions
