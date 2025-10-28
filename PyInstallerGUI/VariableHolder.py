import datetime
from tkinter import ttk
from tkinter import IntVar
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
    CtrlPressed = False
    Direction=0
    LoadPreviousRunMode = False 
    PreviousLoadedDataDump = None
    PreviousLoadedDataIsLegacy= False #This is to check if the loaded data is from a version before we added the software version saving

class ManualResData:
    ChosenPointsHor = [[],[]]
    ChosenPointsVert = [[],[]]
    HoleSize = None
    Image = None
    ContrastResponse = None
    LineData = None
    def __init__(self):
        self.ChosenPointsXPeaks = [[],[]] #0 = hor 1 = vert
        self.ChosenPointsYPeaks = [[],[]]
        self.ChosenPointsXTroughs = [[],[]] #0 = hor 1 = vert
        self.ChosenPointsYTroughs = [[],[]]
        self.HoleSize = None
        self.Image = None
        self.ContrastResponse = None
        self.LineData = None