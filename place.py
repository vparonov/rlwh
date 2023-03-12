class Place:
    
    def __init__(self, capacity = 1):
        self.capacity = capacity
        self.values = set()
        
    def Add(self, value):
        if self.capacity > 0 and len(self.values) == self.capacity:
            raise ValueError("Place is full")
        
        self.values.add(value)
    
    def Remove(self):
        return self.values.pop()
    
    def IsEmpty(self):
        return len(self.values) == 0

    def __len__(self):
        return len(self.values)
    
    def __iter__(self):
        return iter(self.values)
    
    def __contains__(self, value):
        return value in self.values
    
    def __str__(self):
        return str(self.values)
    
    def __repr__(self):
        return str(self.values)
    

    