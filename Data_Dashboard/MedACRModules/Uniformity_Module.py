
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_uniformity import ACRUniformity
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

class UniformityModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        

    def Run(self):
        print("Running Uniformity")
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]
        acr_uniformity_task = ACRUniformity(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True,Paramater_overide = ParamaterOverides)
        self.results=acr_uniformity_task.run()

    def GetReportText(self):

        print(" Uniformity :" + str(self.results["measurement"]["integral uniformity %"]))
        Text=""
        Text+=( '\tUniformity:  %-12s%-12s' % (str(self.results["measurement"]["integral uniformity %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["integral uniformity %"],"Uniformity") ))
        return Text

    def GetModuleName(self):
        return self.name
