from scheduler import Scheduler

class Simulator:
    def __init__(self):
        self.Reset()    

    def Reset(self):
        self.scheduler = Scheduler()
        self.t = 0 

    def Step(self,  t, components):
        try:
            self.t += 1
            iterations = self.scheduler.Execute(t)  
            for c in components:  
                c.ScheduleTransitions(self.scheduler, t)
            iterations += self.scheduler.Execute(t) 
        except Exception as e:
            return False, iterations, e 
        
        return True, iterations, None

if __name__ == "__main__":
    from conveyor import Conveyor
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
                if currentTime % 2 == 0:
                    self.last_value = FIFO
                else:
                    self.last_value = SKIP

            return self.last_value
        
    source = Source('SOURCE', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'], simpleSource())
    c1 = Conveyor('C1', 10, 0)
    sink = Sink('SINK')

    source.Connect(c1.FirstPlace())
    c1.Connect(sink.FirstPlace())

    components = [source, c1, sink]

    for t in range(25):
        ok, iterations, e, = simulator.Step(t, components)
        if not ok:
            print(e)
            break
        print(iterations, t, c1, sink) 
