from hazenlib.logger import logger

ToleranceTable = {}
ToleranceTable["SNR"]=[None,None]
ToleranceTable["Geometric Accuracy"]=[None,None]
ToleranceTable["Uniformity"]=[None,None]
ToleranceTable["Ghosting"]=[None,None]
ToleranceTable["Slice Position"]=[None,None]
ToleranceTable["Slice Thickness"]=[None,None]
ToleranceTable["Spatial Resolution 1.1mm"]=[None,None]
ToleranceTable["Spatial Resolution 1.0mm"]=[None,None]
ToleranceTable["Spatial Resolution 0.9mm"]=[None,None]
ToleranceTable["Spatial Resolution 0.8mm"]=[None,None]
ToleranceTable["Spatial Resolution MTF50 Raw"]=[None,None]
ToleranceTable["Spatial Resolution MTF50 Fitted"]=[None,None]
ToleranceTable["Manual Resolution"]=None

f = open("ToleranceTable/ToleranceTable.txt")
for line in f: 
    if line[0]!="#":
        if "==" not in line:
            Name = line.split(",")[0].strip()
            Lower = line.split(",")[1].strip()
            Upper = line.split(",")[2].strip()
            if Lower == "None" or Lower=="none":
                Lower = None
            else:
                Lower=float(Lower)
            if Upper == "None" or Upper=="none":
                Upper = None
            else:
                Upper=float(Upper)
            if Name not in ToleranceTable.keys():
                logger.error("Unknown test name in the tolerance table")
            ToleranceTable[Name] = [Lower,Upper]
        else:
            Name  = line.split("==")[0]
            Value = line.split("==")[1]
            ToleranceTable[Name] = Value

def GetPassResult(Value,TestName):
    if ToleranceTable[TestName]==[None,None] or ToleranceTable[TestName]==None:
        return "Result: No Tolerance Set"
    Pass=True
    Appendix = []
    AppendixTxt=""
    if type(ToleranceTable[TestName])==list and len(ToleranceTable[TestName])==2:
        if ToleranceTable[TestName][1]!=None:
            if Value > ToleranceTable[TestName][1]:
                Pass=False
            Appendix.append("<"+str(ToleranceTable[TestName][1]))
        if ToleranceTable[TestName][0]!=None:
            if Value < ToleranceTable[TestName][0]:
                Pass=False
            Appendix.append(">"+str(ToleranceTable[TestName][0]))
        
        if len(Appendix) == 1 :
            AppendixTxt = Appendix[0]
        if len(Appendix) == 2 :
            AppendixTxt = Appendix[1] +" and " + Appendix[0]
    else:
        if (ToleranceTable[TestName]!=Value):
            Pass = False
        AppendixTxt = ToleranceTable[TestName]

    if Pass ==True:
        return ("Result: Pass      Tolerance: " + AppendixTxt)
    else:
        return ("Result: Fail      Tolerance: " + AppendixTxt) 