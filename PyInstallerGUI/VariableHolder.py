import datetime
class VarHolder:
    StartingEvent=None
    TimeOfLastEvent = datetime.datetime.now()
    CurrentImage = None
    Canvas = None
    CurrentLevel = None
    CurrentWidth = None
    CurrentROI=None
    ROI_Results_ResResults = {}
    WinLevelLabel=None
    WinWidthLabel=None
    NewWindow = None