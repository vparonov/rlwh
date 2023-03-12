class Transition:
    def __init__(self, 
                placeRegistry, 
                scheduler, 
                delayFn = lambda : 0, 
                actionFn = lambda inputPlaces, outputPlaces: None):
        self.inputPlaces = []
        self.outputPlaces = []
        self.placeRegistry = placeRegistry
        self.scheduler = scheduler
        self.delayFn = delayFn
        self.actionFn = actionFn

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
            if self.placeRegistry.IsFull(inputPlaceID):
                return True
        return False

    def ScheduleExecute(self, currentTime):
        self.scheduler.Enqueue(currentTime + self.delayFn(), 
                               lambda: self.actionFn(self.inputPlaces, self.outputPlaces))

if __name__ == "__main__":
    from placeregistry import PlaceRegistry
    from scheduler import Scheduler


    registry = PlaceRegistry()
    scheduler = Scheduler()

    def testAction(inputPlaces, outputPlaces):
        print(len(inputPlaces), len(outputPlaces))

    transition = Transition(placeRegistry = registry, 
                            scheduler=scheduler,
                            delayFn = lambda : 10, 
                            actionFn = testAction)

    p1 = registry.AddPlace()
    p2 = registry.AddPlace()
    transition.ConnectPlaces(p1, p2)

    transition.ScheduleExecute(0)

    for t in range(20):
        print(t) 
        scheduler.Execute(t)    


#           1         2 
# 012345678901234567890123456789
# p 
#  x
#   p
#    x 