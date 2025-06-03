
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_geometric_accuracy import ACRGeometricAccuracy
from hazenlib.tasks.acr_geometric_accuracy_MagNetMethod import ACRGeometricAccuracyMagNetMethod
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
from MedACROptions import *

class GeoAccModule(MedACRModule):

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
        GeoMethod = self.settings["GeoMethod"]

        if (GeoMethod == GeometryOptions.ACRMETHOD):
            acr_geometric_accuracy_task = ACRGeometricAccuracy(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True,Paramater_overide = ParamaterOverides)
            self.results = acr_geometric_accuracy_task.run()

        if (GeoMethod == GeometryOptions.MAGNETMETHOD):
            acr_geometric_accuracy_MagNetMethod = ACRGeometricAccuracyMagNetMethod(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True, SkipGaussFit=True,Paramater_overide = ParamaterOverides)
            self.results = acr_geometric_accuracy_MagNetMethod.run()

    def GetReportText(self):
        GeoMethod = self.settings["GeoMethod"]
        if (GeoMethod == GeometryOptions.ACRMETHOD):
            print("Slice 1 Hor Dist: "+str(self.results["measurement"][self.results["file"][0]]["Horizontal distance"]) + "   "+ " Vert Dist: "+str(self.results["measurement"][self.results["file"][0]]["Vertical distance"]))
            print("Slice 5 Hor Dist:"+str(self.results["measurement"][self.results["file"][1]]["Horizontal distance"]) + "   "+ " Vert Dist:"+str(self.results["measurement"][self.results["file"][1]]["Vertical distance"])+ "   "+ " Diag SW Dist:"+str(self.results["measurement"][self.results["file"][1]]["Diagonal distance SW"])+ "   "+ "Diag SE Dist:"+str(self.results["measurement"][self.results["file"][1]]["Diagonal distance SE"]))
            Text=""
            Text+=("\tSlice 1:\n")
            Text+=( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(self.results["measurement"][self.results["file"][0]]["Horizontal distance"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][0]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            Text+=( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(self.results["measurement"][self.results["file"][0]]["Vertical distance"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][0]]["Vertical distance"],"Geometric Accuracy","ACRMethod") ))

            Text+=("\tSlice 5:\n")
            Text+=( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(self.results["measurement"][self.results["file"][1]]["Horizontal distance"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][1]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            Text+=( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(self.results["measurement"][self.results["file"][1]]["Vertical distance"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][1]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            Text+=( '\t\tDiagonal distance SW (mm): %-12s%-12s\n' % (str(self.results["measurement"][self.results["file"][1]]["Diagonal distance SW"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][1]]["Diagonal distance SW"],"Geometric Accuracy","ACRMethod") ))
            Text+=( '\t\tDiagonal distance SE (mm): %-12s%-12s' % (str(self.results["measurement"][self.results["file"][1]]["Diagonal distance SE"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"][self.results["file"][1]]["Diagonal distance SE"],"Geometric Accuracy","ACRMethod") ))
            return Text
        if (GeoMethod == GeometryOptions.MAGNETMETHOD):
            print("Horizontal CoV(%):        "+str(self.results["measurement"]["distortion"]["distortion values"]["horizontal CoV"]))
            print("Vertical CoV(%):          "+str(self.results["measurement"]["distortion"]["distortion values"]["vertical CoV"]))
            Text=""
            Text+=( '\t\tHorizontal CoV:     %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["distortion values"]["horizontal CoV"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["distortion values"]["horizontal CoV"],"Geometric Accuracy")))
            Text+=( '\t\tVertical CoV:       %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["distortion values"]["vertical CoV"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["distortion values"]["vertical CoV"],"Geometric Accuracy")))
            Text+=( '\t\tRow Bottom (mm):       %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["horizontal distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["horizontal distances mm"][0],"Geometric Accuracy","MagNetMethod")))
            Text+=( '\t\tRow Middle (mm):    %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["horizontal distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["horizontal distances mm"][1],"Geometric Accuracy","MagNetMethod")))
            Text+=( '\t\tRow Top (mm):    %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["horizontal distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["horizontal distances mm"][2],"Geometric Accuracy","MagNetMethod")))
            Text+=( '\t\tCol Left (mm):       %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["vertical distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["vertical distances mm"][0],"Geometric Accuracy","MagNetMethod")))
            Text+=( '\t\tCol Middle (mm):    %-12s%-12s\n' % (str(self.results["measurement"]["distortion"]["vertical distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["vertical distances mm"][1],"Geometric Accuracy","MagNetMethod")))
            Text+=( '\t\tCol Right (mm):    %-12s%-12s' % (str(self.results["measurement"]["distortion"]["vertical distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["distortion"]["vertical distances mm"][2],"Geometric Accuracy","MagNetMethod")))        
            return Text

    def GetModuleName(self):
        return self.name
