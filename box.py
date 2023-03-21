MAX_STATIONS = 2

class Box:
    def __init__(self, id, route, deadline = -1):
        self.id = id
        self.route = route
        self.pickedMask = 0
        self.deadline = deadline
    
    def IsForStation(self, station):
        return ((self.route & (~self.pickedMask)) & (1 << (station-1))) != 0 

    def Pick(self, station):
        self.pickedMask |= (1 << (station-1))

    def Id(self):
        return self.id
    
    def Reset(self):
        self.pickedMask = 0

    def __repr__(self):
        s = bin(self.route & (~self.pickedMask))[2:]
        s = s.rjust(MAX_STATIONS, '0')
        return f"B(id={self.id}, route={s})"

def BoxListFromFile(fileName):
    boxes = []
    with open(fileName) as file:
        boxes = [Box(*(line.rstrip().split(','))) for line in file]
    return boxes


if __name__ == "__main__":
    b1 = Box(1, 0)    
    b2 = Box(2, 1)
    b3 = Box(3, 2)    
    b4 = Box(4, 3)

    print(b1, b2, b3, b4)
    print('picking b2 at 1 ')
    b2.Pick(1)

    print(b2)
    

    print('picking b3 at 2 ')
    b3.Pick(2)
    print(b3)    

    print('picking b4 at 1 ')  
    b4.Pick(1) 
    print(b4)    
    
    print('picking b4 at 2 ')  
    b4.Pick(2) 
    print(b4)     