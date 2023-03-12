NOT_SCHEDULED = 0
SCHEDULED = 1

class Transition:
    def __init__(self, 
                scheduler, 
                delayFn = lambda : 0, 
                actionFn = lambda inputPlaces, outputPlaces: None):
        self.inputPlaces = []
        self.outputPlaces = []
        self.scheduler = scheduler
        self.delayFn = delayFn
        self.actionFn = actionFn
        self.state = NOT_SCHEDULED 

    # connections 
    def AddInputPlace(self, place):
        self.inputPlaces.append(place)

    def AddOutputPlace(self, place):
        self.outputPlaces.append(place)    

    def ConnectPlaces(self, inputplace, outputplace):
        self.AddInputPlace(inputplace)
        self.AddOutputPlace(outputplace)

    # transactions

    def IsEnabled(self):
        for inputplace in self.inputPlaces:
            if not inputplace.IsEmpty():
                return True
        return False

    def ScheduleExecute(self, currentTime):
        def action(executionTime):
            print(f"Executing at {executionTime}")
            self.actionFn(self.inputPlaces, self.outputPlaces)
            self.state = NOT_SCHEDULED

        if self.state == SCHEDULED:
            return
        self.state = SCHEDULED
        self.scheduler.Enqueue(currentTime + self.delayFn(), task = action)

if __name__ == "__main__":
    from place import Place
    from scheduler import Scheduler
    from transitionfactory import TransitionFactory

    scheduler = Scheduler()

    transitionFactory = TransitionFactory(scheduler)

    def testAction_d(inputPlaces, outputPlaces):
        print('delayed')

    def testAction_0(inputPlaces, outputPlaces):
        print('not delayed')

    transition = transitionFactory.MakeTransition(
                    delayFn = lambda : 10, 
                    actionFn = testAction_d)

    transition0 = transitionFactory.MakeTransition(
                    delayFn = lambda : 0, 
                    actionFn = testAction_0)

    p1 = Place(1)
    p2 = Place(1)
    p3 = Place(1)

    p1.Add('A')
   
    transition.ConnectPlaces(p1, p2)
    transition0.ConnectPlaces(p2, p3)
  
    for t in range(25):
        print(t) 
        scheduler.Execute(t)    
        for transition in transitionFactory.GetTransitions():
            if transition.IsEnabled():
                transition.ScheduleExecute(t)
        scheduler.Execute(t)    


#           1         2 
# 012345678901234567890123456789
# p 
#  x
#   p
#    x 