import datetime
class VarHolder:
    StartingEvent=None
    TimeOfLastEvent = datetime.datetime.now()
    CurrentImage = None
    Canvas = None
    CurrentLevel = None
    CurrentWidth = None
    CurrentROI=None
    #ROI_Results_ResResults = {}
    WinLevelLabel=None
    WinWidthLabel=None
    WinDirectionLabel=None
    NewWindow = None
    WidthChange=0
    LevelChange=0
    ManualResData={}
    ShiftPressed = False
    Direction=0

class ManualResData:
    ChosenPointsHor = [[],[]]
    ChosenPointsVert = [[],[]]
    HoleSize = None
    Image = None
    ContrastResponse = None
    LineData = None
    def __init__(self):
        self.ChosenPointsX = [[],[]] #0 = hor 1 = vert
        self.ChosenPointsY = [[],[]]
        self.HoleSize = None
        self.Image = None
        self.ContrastResponse = None
        self.LineData = None