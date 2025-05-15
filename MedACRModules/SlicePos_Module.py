
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_slice_position import ACRSlicePosition
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

class SlicePosModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        
    def Run(self):
        print("Running Slice Position")
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]
        acr_slice_position_task = ACRSlicePosition(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,Paramater_overide = ParamaterOverides)
        self.results = acr_slice_position_task.run()

        #Divide by 2 to get the true error in slice position.
        self.results['measurement'][self.results['file'][0]]['length difference'] = round(self.results['measurement'][self.results['file'][0]]['length difference']/2.0,2)
        self.results['measurement'][self.results['file'][1]]['length difference'] = round(self.results['measurement'][self.results['file'][1]]['length difference']/2.0,2)


    def GetReportText(self):
        print("Slice Pos difference " + self.results['file'][0] + " :" + str(self.results['measurement'][self.results['file'][0]]['length difference']) + "mm    " + self.results['file'][1] + " :" + str(self.results['measurement'][self.results['file'][1]]['length difference'])+"mm")
        Text=""
        Text+=( '\tSlice 1 Position Error (mm):  %-12s%-12s\n' % (str(self.results['measurement'][self.results['file'][0]]['length difference']),MedACR_ToleranceTableChecker.GetPassResult(self.results['measurement'][self.results['file'][0]]['length difference'],"Slice Position") ))
        Text+=( '\tSlice 11 Position Error (mm): %-12s%-12s' % (str(self.results['measurement'][self.results['file'][1]]['length difference']),MedACR_ToleranceTableChecker.GetPassResult(self.results['measurement'][self.results['file'][1]]['length difference'],"Slice Position") ))
        return Text

    def GetModuleName(self):
        return self.name
