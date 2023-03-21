import numpy as np

from place import Place
from transition import Transition
from scheduler import BLOCKED, FINISHED, PHASE_MAIN, PHASE_SECONDARY

SKIP = 0
FIFO = 1 

class Source:
    def __init__(self, name, values, sourceFn):
        self.name = name
        self.sourceFn = sourceFn
        self.inputPlace = None
        self.transition = None

        self.make()
        self.Reset(values)

    def make(self):
        def sourceTransitionFn(inputPlaces, outputPlaces, currentTime, phase):
            if len(outputPlaces) == 0:
                return FINISHED
            
            outputPlace = outputPlaces[0]

            if outputPlace.IsDisabled():
                return FINISHED
            
            action = self.sourceFn(currentTime)

            if action == SKIP:
                return FINISHED
            
            if action != FIFO:
                raise Exception("Invalid source action: %s" % action)
            
            inputPlace = inputPlaces[0]
            if inputPlace.IsEmpty():
                return FINISHED
            
          
            if phase == PHASE_MAIN:
                # during the main phase, try to put the value only if the output place is empty
                if not outputPlace.IsFull() :
                    v = inputPlace.Remove()
                    outputPlace.Add(v)
                    return FINISHED
                else:
                    return BLOCKED
            else:
                # during the secondary phase, try to put the value even if the output place is not empty
                # should fail (with exception) if outputPlace is not empty
                v = inputPlace.Remove()
                outputPlace.Add(v)

        self.inputPlace = Place(capacity= -1) # -1 means infinite
                                     # no  delay 
        self.transition = Transition(lambda: 0, sourceTransitionFn)
        self.transition.AddInputPlace(self.inputPlace)

    def State(self):
        state = np.asarray([len(self.inputPlace)])
        return state
    
    def Capacity(self):
        return 1  
    
    def Connect(self, nextPlace):
        _, countOutputPlaces = self.transition.CountPlaces()
        if countOutputPlaces > 0:
            raise Exception(f"The source {self.name} is already connected")
        
        self.transition.AddOutputPlace(nextPlace) 

    def Reset(self, values):
        self.inputPlace.SetValues(values) 
        self.currentAction = None 

    def ScheduleTransitions(self, scheduler, t):
        if self.transition.IsEnabled():
            self.transition.ScheduleExecute(scheduler, t)


if __name__ == "__main__":
    from conveyor import Conveyor
    from scheduler import Scheduler
    from sink import Sink
 
    class simpleSource:
        def __init__(self):
            pass  

        def __call__(self, currentTime):
            print(f'current time: {currentTime}')
            if currentTime % 1 == 0:
                return FIFO
            else:
                return SKIP
    
    scheduler = Scheduler()
                
    evenH = simpleSource()
    s = Source('S', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'], evenH)
    c = Conveyor('C1', 10, 0)
    sink = Sink('SINK')

    s.Connect(c.FirstPlace())
    c.Connect(sink.FirstPlace())

    try:
        for t in range(25):
            iterations = scheduler.Execute(t)    
            # 
            # here agents interact with the system
            #
            # 
            s.ScheduleTransitions(scheduler, t)
            c.ScheduleTransitions(scheduler, t)
            sink.ScheduleTransitions(scheduler, t)
            iterations += scheduler.Execute(t) 
            print(iterations, t, c, sink) 
    except Exception as e:
        print(t, e)