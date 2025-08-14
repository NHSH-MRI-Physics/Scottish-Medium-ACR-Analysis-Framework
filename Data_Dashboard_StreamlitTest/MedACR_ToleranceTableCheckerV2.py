#from hazenlib.logger import logger
from xml.dom import minidom
import sys
from dataclasses import dataclass

@dataclass
class Tolerance:
    min: float = None
    max: float =None
    equals: float =None

ToleranceTable = {}
def SetUpToleranceTable():
    
    file = minidom.parse('ToleranceTable/ToleranceTable.xml')
    Modules = file.getElementsByTagName('Module')

    for Module in Modules:
        ToleranceTable[Module.attributes['name'].value] = {}
        for child in Module.childNodes:
            if child.nodeName == "Test":
                Max=None
                Min=None
                Equal=None
                Name=None
                if "name" in child.attributes.keys():
                    Name=child.attributes["name"].value
                else:
                    Name = Module.attributes['name'].value

                for key in child.attributes.keys():
                    if key == "Max":
                        Max = float(child.attributes["Max"].value)
                    elif key == "Min":
                        Min = float(child.attributes["Min"].value)
                    elif key == "Equal":
                        if (child.attributes["Equal"].value.replace(".","").isnumeric()):
                            Equal = float(child.attributes["Equal"].value)
                        else:
                            Equal = str(child.attributes["Equal"].value)
                    elif key=="name":
                        pass
                    else:
                        raise Exception("Unexpected attribute in tolerance table. ModuleName: " + str(Module.attributes['name'].value))

                if Min != None and Equal!=None:
                    raise Exception("Error: Tolerance table can't contain both Min and Equal tolerances.")
                if Max != None and Equal!=None:
                    raise Exception("Error: Tolerance table can't contain both Max and Equal tolerances.")

                if Name in ToleranceTable[Module.attributes['name'].value].keys():
                    raise Exception("Mulitple tests need a name attribute!")
                ToleranceTable[Module.attributes['name'].value][Name] = Tolerance(min=Min, max=Max, equals=Equal)

def GetTolerance(ModuleName,TestName=None):
    if TestName==None:
        TestName=ModuleName
    if ModuleName not in ToleranceTable.keys():
        return None
    if TestName not in ToleranceTable[ModuleName].keys():
        return None
    return ToleranceTable[ModuleName][TestName]

def GetPassResult(Value,ModuleName,TestName=None):
    if TestName==None:
        TestName=ModuleName

    if ModuleName not in ToleranceTable.keys():
        return "Result: No Tolerance Set"

    if TestName not in ToleranceTable[ModuleName].keys():
        return "Result: No Tolerance Set"


    Pass=True
    Appendix = []
    AppendixTxt=""

    if ToleranceTable[ModuleName][TestName].equals!=None:
        if ToleranceTable[ModuleName][TestName].equals!=Value:
            Pass=False
        AppendixTxt = ToleranceTable[ModuleName][TestName].equals
    else:
        if ToleranceTable[ModuleName][TestName].min!=None:
            if Value < ToleranceTable[ModuleName][TestName].min:
                Pass=False
            Appendix.append(">"+str(ToleranceTable[ModuleName][TestName].min))
        if ToleranceTable[ModuleName][TestName].max!=None:
            if Value > ToleranceTable[ModuleName][TestName].max:
                Pass=False
            Appendix.append("<"+str(ToleranceTable[ModuleName][TestName].max))
        
        if len(Appendix) == 1 :
            AppendixTxt = Appendix[0]
        if len(Appendix) == 2 :
            AppendixTxt = Appendix[0] +" and " + Appendix[1]

    if Pass == True:
        return ("Result: Pass      Tolerance: " + AppendixTxt)
    else:
        return ("Result: Fail      Tolerance: " + AppendixTxt) 