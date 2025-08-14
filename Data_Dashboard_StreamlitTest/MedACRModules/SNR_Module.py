
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_snr import ACRSNR
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

class SNRModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        

    def Run(self):
        print("Running SNR")
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]

        acr_snr_task = ACRSNR(input_data=Data, report_dir=OutputPath,report=True,MediumACRPhantom=True,Paramater_overide = ParamaterOverides)
        self.results = acr_snr_task.run()

    def GetReportText(self):
        print("SNR :" +str(self.results["measurement"]["snr by smoothing"]["measured"]))
        print("Normalised SNR :" +str(self.results["measurement"]["snr by smoothing"]["normalised"]))
        
        Text=""
        Text+=( '\tSNR:            %-12s%-12s\n' % (str(self.results["measurement"]["snr by smoothing"]["measured"]), MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["snr by smoothing"]["measured"],"SNR")))
        Text+=( '\tNormalised SNR: %-12s%-12s' % (str(self.results["measurement"]["snr by smoothing"]["normalised"]), MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["snr by smoothing"]["normalised"],"SNR")))
        return Text

    def GetModuleName(self):
        return self.name
