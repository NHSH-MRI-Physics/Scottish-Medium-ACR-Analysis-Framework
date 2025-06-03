
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_ghosting import ACRGhosting
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

class GhostingModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        

    def Run(self):
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]

        print("Running Ghosting")
        acr_ghosting_task = ACRGhosting(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True,Paramater_overide = ParamaterOverides)
        self.results = acr_ghosting_task.run()



    def GetReportText(self):
        print("Ghosting :" + str(self.results["measurement"]["signal ghosting %"]))
        
        Text = ""
        Text+=( '\tGhosting:    %-12s%-12s' % (str(self.results["measurement"]["signal ghosting %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["signal ghosting %"],"Ghosting") ))
        return Text

    def GetModuleName(self):
        return self.name
