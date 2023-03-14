from collections import defaultdict

BLOCKED = -1
FINISHED = 1

PHASE_MAIN = 0
PHASE_SECONDARY = 1

class Scheduler:
    def __init__(self):
        self.queue = defaultdict(lambda: None)

    def Enqueue(self, at, task):
        if self.queue[at] is None:
            self.queue[at] = [task]
        else:
            self.queue[at].append(task)

    def Execute(self, at):
        if self.queue[at] is None:
            return
        
        someFinished = True
        while someFinished:
            someFinished = False 
            for task in self.queue[at]:
                result = task(at, PHASE_MAIN)
                if result == FINISHED:
                    someFinished = True
                    self.queue[at].remove(task)
        
        someFinished = True
        while someFinished:
            someFinished = False 
            for task in self.queue[at]:
                result = task(at, PHASE_SECONDARY)
                if result == FINISHED:
                    someFinished = True
                    self.queue[at].remove(task)
        
        del self.queue[at]
    

if __name__ == '__main__':
    s = Scheduler()
    s.Enqueue(1, lambda t : print('1.1'))
    s.Enqueue(1, lambda t : print('1.2'))
    s.Enqueue(2, lambda t: print('2'))
    s.Enqueue(10, lambda t: print('10'))

    for i in range(11):
        s.Execute(i)
   