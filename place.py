class Place:
    
    def __init__(self, capacity = 1):
        self.capacity = capacity
        self.disabled = False
        self.values = []
        
    def Add(self, value):
        if self.capacity > 0 and len(self.values) == self.capacity:
            raise ValueError("Place is full")
        
        self.values.append(value)
    def Remove(self):
        return self.values.pop(0)
    
    def Clear(self):
        self.values = []

    def SetValues(self, values):
        self.values = values.copy()

    def Disable(self):
        self.disabled = True

    def Enable(self):
        self.disabled = False
    
    def IsDisabled(self):
        return self.disabled == True
    
    def IsEmpty(self):
        return len(self.values) == 0
    
    def IsFull(self):
        return len(self.values) == self.capacity
    
    def __getitem__(self, key):
        return self.values[key]
    
    def __len__(self):
        return len(self.values)
    
    def __str__(self):
        return str(self.values)
    
if __name__ == "__main__":
    p = Place(2)

    p.Add('A')
    p.Add('B')


    print(p.IsEmpty())

    print(p.Remove())  
    print(p.Remove())

    print(p.IsEmpty())