import shapely
import matplotlib.pyplot as plt

class Strucutre:
    def __init__(self, x, y, radius,signal): #This is in mm
        self.x = x
        self.y = y
        self.radius = radius
        self.signal = signal
        self.circle = shapely.Point(self.x, self.y).buffer(self.radius)


def TestCircle(dxy,res):
    Background = Strucutre(0,0,100,0.5)
    Circle = Strucutre(0,0,5,0.75)
    Phantom = [Background,Circle]
    x = -res*dxy
    y = -res*dxy
    for i in range(res):
        for j in range(res):
            PixelBounds = shapely.box(x,y,x+res*dxy,y+res*dxy) #[x,y,x+res*dxy,y+res*dxy]
            x,y = PixelBounds.exterior.xy
            plt.plot(x,y)
    plt.show()