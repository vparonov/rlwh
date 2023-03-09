class Transition:
    def __init__(self, placeRegistry, delayFn = lambda : 0):
        self.inputPlaces = []
        self.outputPlaces = []
        self.placeRegistry = placeRegistry
        self.delayFn = delayFn


    def AddInputPlace(self, placeID):
        self.inputPlaces.append(placeID)

    def AddOutputPlace(self, placeID):
        self.outputPlaces.append(placeID)    

    def ConnectPlaces(self, inputPlaceID, outputPlaceID):
        self.AddInputPlace(inputPlaceID)
        self.AddOutputPlace(outputPlaceID)

if __name__ == "__main__":
    from placeregistry import PlaceRegistry

    registry = PlaceRegistry()
    transition = Transition(placeRegistry = registry, delayFn = lambda : 50)
    print(f'delay = {transition.delayFn()}')

    p1 = registry.AddPlace()
    p2 = registry.AddPlace()
    transition.ConnectPlaces(p1, p2)
    
