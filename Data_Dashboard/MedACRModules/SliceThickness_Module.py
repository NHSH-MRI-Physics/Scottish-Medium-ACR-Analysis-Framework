
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_slice_thickness import ACRSliceThickness
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

class SliceThicknessModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        

    def Run(self):
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]
        UseLegacySliceThicknessAlgo = self.settings["UseLegacySliceThicknessAlgo"]

        print("Running Slice Thickness")
        acr_slice_thickness_task = ACRSliceThickness(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,Paramater_overide = ParamaterOverides, UseLegacySliceThicknessAlgo=UseLegacySliceThicknessAlgo)
        self.results = acr_slice_thickness_task.run()


    def GetReportText(self):
        print("Slice Width (mm): " + str(self.results['measurement']['slice width mm']))
        Text = ""
        Text+=( '\tSlice Width (mm): %-12s%-12s' % (str(self.results['measurement']['slice width mm']),MedACR_ToleranceTableChecker.GetPassResult(self.results['measurement']['slice width mm'],"Slice Thickness") ))
        return Text


    def GetModuleName(self):
        return self.name
