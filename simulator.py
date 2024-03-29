from scheduler import Scheduler

class Simulator:
    def __init__(self):
        self.Reset()    

    def Reset(self):
        self.scheduler = Scheduler()

    def Step(self,  t, components):
        iterations = 0 
        for c in components:  
            c.ScheduleTransitions(self.scheduler, t)
        iterations = self.scheduler.Execute(t) 

        return iterations

if __name__ == "__main__":
    import numpy as np
    from conveyor import Conveyor
    from diverter import Diverter, CONTINUE_STRAIGHT, DIVERT, FORWARD, BACKWARD
    from box import Box
    from sink import Sink
    from source import Source, SKIP, FIFO 
   
    simulator = Simulator()

    class simpleSource:
        def __init__(self):
            self.last_t = -1
            self.last_value = -1 

        def __call__(self, currentTime):
            if currentTime != self.last_t:
                self.last_t = currentTime           
                if currentTime % 1 == 0:
                    self.last_value = FIFO
                else:
                    self.last_value = SKIP

            return self.last_value
        
    items = []
    for i in range(10):
        items.append(Box(i, 's', 3))

    source = Source('SOURCE', items, simpleSource())
    c1 = Conveyor('C1', 10, 0)
    s01 = Conveyor('S01', 5, 0)
    d1 = Diverter('D1', 
                  delay = 0, 
                  type= BACKWARD, 
                  selectorFn = lambda box: DIVERT if box.IsForStation(1) else CONTINUE_STRAIGHT)
    
    sink = Sink('SINK')

    source.Connect(c1.FirstPlace())
    sink.SetCapacity(source.Capacity())
    c1.Connect(d1.FirstPlace())
    d1.Connect(sink.FirstPlace(), s01.FirstPlace())

    components = [source, c1, d1, s01, sink]

    for t in range(15):
        try:
            iterations = simulator.Step(t, components)
            states = [np.sum(c.State())/c.Capacity() for c in components]
            print(states)
            print(t)
            print(c1)
            print(d1)
            print(s01)
            print(sink) 
            if states[-1] == 1.0:
                print('finished')
                break 
        except Exception as e:
            print(e)
            break 