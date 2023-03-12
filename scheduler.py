from collections import defaultdict

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
        for task in self.queue[at]:
            task()
        del self.queue[at]
    

if __name__ == '__main__':
    s = Scheduler()
    s.Enqueue(1, lambda: print('1.1'))
    s.Enqueue(1, lambda: print('1.2'))
    s.Enqueue(2, lambda: print('2'))
    s.Enqueue(10, lambda: print('10'))

    for i in range(11):
        s.Execute(i)
   