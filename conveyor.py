from place import Place
from transition import Transition

BEGINNING = 0
END = 1
ANYWHERE = -1

class Conveyor:
    def __init__(self, name, capacity, delay=0):
        self.capacity = capacity
        self.delayFn = lambda: delay
        self.name = name
        self.enabled = True
        self.places = []
        self.transitions = []

        self.make()

    def make(self):
        def conveyorTransitionFn(inputPlaces, outputPlaces):
            if len(outputPlaces) == 0:
                return 
            
            if self.IsStopped():
                return 
            
            outputPlace = outputPlaces[0]

            if outputPlace.IsDisabled():
                return 
            
            inputPlace = inputPlaces[0]
            
            if outputPlace.IsEmpty() :
                v = inputPlace.Remove()
                outputPlace.Add(v)

        prevTransition = None
        for _ in range(self.capacity):
            newPlace  = Place(capacity=1)
            newTransition = Transition(self.delayFn, conveyorTransitionFn)
            self.places.append(newPlace)
            self.transitions.append(newTransition)

            newTransition.AddInputPlace(newPlace)
            if prevTransition is not None:
                prevTransition.AddOutputPlace(newPlace)

            prevTransition = newTransition

    def Connect(self, nextPlace):
        _, countOutputPlaces = self.transitions[-1].CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The conveyor {self.name} is already connected")
        
        self.transitions[-1].AddOutputPlace(nextPlace) 

    def ScheduleTransitions(self, scheduler, t):
        for transition in self.Transitions():
            if transition.IsEnabled():
                transition.ScheduleExecute(scheduler, t)

    def FirstPlace(self):
        return self.places[0]
    
    def Stop(self):
        self.enabled = False
        self.places[0].Disable()

    def Start(self):
        self.enabled = True
        self.places[0].Enable()
 
    def IsStopped(self):
        return self.enabled == False
    
    def Reset(self):
        for place in self.places:
            if len(place) > 0:
                place.Remove()
        self.Start()

    def Transitions(self):
        return self.transitions
      
    def PutValue(self, value, where = BEGINNING):
        if where == BEGINNING:
            self.places[0].Add(value)
        elif where == ANYWHERE:
            for place in self.places:
                if place.IsEmpty():
                    place.Add(value)
                    break
        else:
            raise Exception(f"Invalid where {where}")
        
    def GetValue(self, where = BEGINNING):
        if where == BEGINNING:
            return self.places[0].Remove()
        elif where == END:
            return self.places[0].Remove()
        elif where == ANYWHERE:
            for place in self.places:
                if not place.IsEmpty():
                    return place.Remove()
        else:
            raise Exception(f"Invalid where {where}")

    def __str__(self):
        s = f'{self.name}:'
        for place in self.places:
            s += f' {place}'
        return s

if __name__ == "__main__":
    from scheduler import Scheduler

    scheduler = Scheduler()

    c = Conveyor("c1", 10, 0)

    c2 = Conveyor("c2", 10, 0)

    c.Connect(c2.FirstPlace())

    c2.Stop()
    c.PutValue('A')
    print(c)

    for t in range(25):
       
        if t == 22:
            c2.Start()
        scheduler.Execute(t)    
        c.ScheduleTransitions(scheduler, t)
        c2.ScheduleTransitions(scheduler, t)
        scheduler.Execute(t) 
        print(t, c, c2) 

