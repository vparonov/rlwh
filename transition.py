NOT_SCHEDULED = 0
SCHEDULED = 1

class Transition:
    def __init__(self, 
                delayFn = lambda : 0, 
                actionFn = lambda inputPlaces, outputPlaces, phase: None):
        self.inputPlaces = []
        self.outputPlaces = []
        self.delayFn = delayFn
        self.actionFn = actionFn
        self.state = NOT_SCHEDULED 

    # connections 
    def AddInputPlace(self, place):
        self.inputPlaces.append(place)

    def AddOutputPlace(self, place):
        self.outputPlaces.append(place)    

    def CountPlaces(self):
        return len(self.inputPlaces), len(self.outputPlaces)
    
    def ConnectPlaces(self, inputplace, outputplace):
        self.AddInputPlace(inputplace)
        self.AddOutputPlace(outputplace)

    # transactions

    def IsEnabled(self):
        for inputplace in self.inputPlaces:
            if not inputplace.IsEmpty():
                return True
        return False

    def ScheduleExecute(self, scheduler, currentTime):
        def action(executionTime, phase):
            res = self.actionFn(self.inputPlaces, self.outputPlaces, phase)
            self.state = NOT_SCHEDULED
            return res 

        if self.state == SCHEDULED:
            return
        self.state = SCHEDULED
        scheduler.Enqueue(currentTime + self.delayFn(), task = action)

if __name__ == "__main__":
    from place import Place
    from scheduler import Scheduler
   
    scheduler = Scheduler()

    def testAction_d(inputPlaces, outputPlaces):
        inputPlace = inputPlaces[0]
        outputPlace = outputPlaces[0]

        if outputPlace.IsEmpty():
            v = inputPlace.Remove()
            outputPlace.Add(v)

    transitions = []
    transition = Transition(
                    delayFn = lambda : 10, 
                    actionFn = testAction_d)

    transition0 = Transition(
                    delayFn = lambda : 0, 
                    actionFn = testAction_d)

    transitions.append(transition)
    transitions.append(transition0)

    p1 = Place(1)
    p2 = Place(1)
    p3 = Place(1)

    p1.Add('A')
    p2.Add('B')

    transition.ConnectPlaces(p1, p2)
    transition0.ConnectPlaces(p2, p3)
  
    for t in range(25):
        print(t) 
        scheduler.Execute(t)    
        for transition in transitions:
            if transition.IsEnabled():
                transition.ScheduleExecute(scheduler, t)
        scheduler.Execute(t)    
        print(p1, p2, p3)

# a | b | c

# v = a[0]
# t.group().remove(a).set(b, v).end()

# v = b[0]
# t.remove(b)
# t.set(c, v)

# groups[g1].append(a)
# groups[g1].append(b)

# ops[a].AddRemoveCmd(g1)
# ops[b].AddSetCmd(v, g1)

# groups[g2].append(b)
# groups[g2].append(c)

# ops[b].AddRemoveCmd(g2)
# ops[c].AddSetCmd(v, g2)


# groups[g1] = [a, b]
# groups[g2] = [b, c]

# ops[a] = {
#     'RemoveCmds': ['g1'],
# }

# ops[b] = {
#     'RemoveCmds': ['g2'],
#     'SetCmds': [(v, 'g1')],
# }

# ops[c] = {
#     'SetCmds': [(v, 'g2')],
# }