
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_uniformity import ACRUniformity
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
from MedACROptions import UniformityOptions
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
        acr_uniformity_task.UniformityMethod = self.settings["UniformityMethod"]
        self.results=acr_uniformity_task.run()

    def GetReportText(self):        
        if self.settings["UniformityMethod"] == UniformityOptions.ACRMETHOD:
            print(" Uniformity :" + str(self.results["measurement"]["integral uniformity %"]))
            Text="\tMethod: ACR Method\n"
            Text+=( '\tUniformity:  %-12s%-12s' % (str(self.results["measurement"]["integral uniformity %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["integral uniformity %"],"Uniformity","ACRMethod") ))
            return Text
        if self.settings["UniformityMethod"] == UniformityOptions.MAGNETMETHOD:
            print("Horizontal Uniformity: " + str(self.results["measurement"]["Horizontal Uniformity %"]))
            print("Vertical Uniformity: " + str(self.results["measurement"]["Vertical Uniformity %"]))
            Text="\tMethod: MagNet Method\n"
            Text+=( '\tHorizontal Uniformity:  %-12s%-12s\n' % (str(self.results["measurement"]["Horizontal Uniformity %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["Horizontal Uniformity %"],"Uniformity","MagNetMethodHor") ))
            Text+=( '\tVertical Uniformity:  %-12s%-12s' % (str(self.results["measurement"]["Vertical Uniformity %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["Vertical Uniformity %"],"Uniformity","MagNetMethodVert") ))
            return Text

    def GetModuleName(self):
        return self.name
