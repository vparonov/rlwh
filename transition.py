NOT_SCHEDULED = 0
SCHEDULED = 1

class Transition:
    def __init__(self, 
                placeRegistry, 
                scheduler, 
                delayFn = lambda : 0, 
                actionFn = lambda placeRegistry, inputPlaces, outputPlaces: None):
        self.inputPlaces = []
        self.outputPlaces = []
        self.placeRegistry = placeRegistry
        self.scheduler = scheduler
        self.delayFn = delayFn
        self.actionFn = actionFn
        self.state = NOT_SCHEDULED 

    # connections 
    def AddInputPlace(self, placeID):
        self.inputPlaces.append(placeID)

    def AddOutputPlace(self, placeID):
        self.outputPlaces.append(placeID)    

    def ConnectPlaces(self, inputPlaceID, outputPlaceID):
        self.AddInputPlace(inputPlaceID)
        self.AddOutputPlace(outputPlaceID)

    # transactions

    def IsEnabled(self):
        for inputPlaceID in self.inputPlaces:
            if not self.placeRegistry[inputPlaceID].IsEmpty():
                return True
        return False

    def ScheduleExecute(self, currentTime):
        def action(executionTime):
            print(f"Executing at {executionTime}")
            self.actionFn(self.placeRegistry, self.inputPlaces, self.outputPlaces)
            self.state = NOT_SCHEDULED

        if self.state == SCHEDULED:
            return
        self.state = SCHEDULED
        self.scheduler.Enqueue(currentTime + self.delayFn(), task = action)

if __name__ == "__main__":
    from placeregistry import PlaceRegistry
    from scheduler import Scheduler
    from transitionfactory import TransitionFactory

    registry = PlaceRegistry()
    scheduler = Scheduler()

    transitionFactory = TransitionFactory(registry, scheduler)

    def testAction_d(placeRegistry, inputPlaces, outputPlaces):
        print('delayed')

    def testAction_0(placeRegistry, inputPlaces, outputPlaces):
        print('not delayed')

    transition = transitionFactory.MakeTransition(
                    delayFn = lambda : 10, 
                    actionFn = testAction_d)

    transition0 = transitionFactory.MakeTransition(
                    delayFn = lambda : 0, 
                    actionFn = testAction_0)

    p1 = registry.AddPlace()
    p2 = registry.AddPlace()
    p3 = registry.AddPlace()

    registry[p1].Add('A')
   
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