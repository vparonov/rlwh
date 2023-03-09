class PlaceRegistry:
    def __init__(self):
        self.places = []

    def AddPlace(self, initialValue = None):
        self.places.append(initialValue)
        return len(self.places) - 1
    
    def AddPlaces(self, count, initialValues = []):
        firstIndex = len(self.places)
        useInitialValues = False
        if len(initialValues) > 0:
            useInitialValues = True
        for i in range(count):
            initialValue = None 
            if useInitialValues:
                initialValue = initialValues[i]
            lastIndex = self.AddPlace(initialValue)
        return firstIndex, lastIndex
    
    def GetValue(self, index):
        return self.places[index]
    
    def SetValue(self, index, value):
        self.places[index] = value
        