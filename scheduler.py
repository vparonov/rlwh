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
            return 0
        
        iterations = 0 
        someFinished = True
        while someFinished:
            someFinished = False 
            for task in self.queue[at]:
                iterations+=1
                result = task(at, PHASE_MAIN)
                if result == FINISHED:
                    someFinished = True
                    self.queue[at].remove(task)
        
        someFinished = True
        while someFinished:
            someFinished = False 
            for task in self.queue[at]:
                if not task.enableSecondaryPhase:
                    continue
                iterations+=1
                result = task(at, PHASE_SECONDARY)
                if result == FINISHED:
                    someFinished = True
                    self.queue[at].remove(task)
        
        # all blocked tasks are rescheduled for the next time slot
        for task in self.queue[at]:
            self.Enqueue(at+1, task)

        del self.queue[at]
        return iterations
    

if __name__ == '__main__':
    s = Scheduler()
    s.Enqueue(1, lambda t,p : FINISHED)
    s.Enqueue(1, lambda t,p : FINISHED)
    s.Enqueue(2, lambda t,p: FINISHED)
    s.Enqueue(10, lambda t,p: FINISHED)

    for i in range(11):
        s.Execute(i)
   