
from MedACRModules.MedACRModuleAbstract import MedACRModule
class EmptyModule(MedACRModule):

    def __init__(self,name):
        self.name = name
        super(MedACRModule,self).__init__()

    def Run(self):
        pass

    def GetReportText(self):
        return "\tNot Run"
    
    def GetModuleName(self):
        return self.name
