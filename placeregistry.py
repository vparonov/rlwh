from place import Place

class PlaceRegistry:
    def __init__(self):
        self.places = []

    def AddPlace(self, capacity  = -1):
        self.places.append(Place(capacity))
        return len(self.places) - 1
    
    def AddPlaces(self, count, capacity = -1):
        firstIndex = len(self.places)
        for i in range(count):
            lastIndex = self.AddPlace(Place(capacity))
        return firstIndex, lastIndex
    
    def __getitem__(self, index):
        return self.places[index]    
    

if __name__ == "__main__":
    registry = PlaceRegistry()
    
    p1 = registry.AddPlace(1)
    p2 = registry.AddPlace(2)
    p3 = registry.AddPlace()


    registry[p1].Add(1)
    
    registry[p2].Add(2)
    registry[p2].Add(3)

    registry[p3].Add(4)
    registry[p3].Add(5)
    registry[p3].Add(6)
    registry[p3].Add(7)
    registry[p3].Add(8)


    print(len(registry[p1]))
    print(registry[p1][0])
    
    