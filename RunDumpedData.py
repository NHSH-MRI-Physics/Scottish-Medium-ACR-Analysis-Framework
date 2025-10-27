import pickle
import os 
import sys
from datetime import date
#from MedACRModules.SNR_Module import SNRModule
#from MedACRModules.Geo_Acc_Module import GeoAccModule
#from MedACRModules.Uniformity_Module import UniformityModule
#from MedACRModules.SlicePos_Module import SlicePosModule
#from MedACRModules.Ghosting_Module import GhostingModule
#from MedACRModules.SliceThickness_Module import SliceThicknessModule
#from MedACRModules.Spatial_res_Module import SpatialResModule
from MedACRModules.Empty_Module import EmptyModule
import MedACRAnalysisV2
import shutil
def RunDumpedData(DumpFile,OutFolder):
    with open(DumpFile, 'rb') as f:
        data = pickle.load(f)

    if not os.path.exists("TempDICOM"):
        os.makedirs("TempDICOM")

    DICOMData = data["DICOM"]
    Seq = DICOMData[0].SeriesDescription
    DICOMS = []
    count = 1
    for DICOM in data["DICOM"]:
        DICOM.save_as(os.path.join("TempDICOM",str(count)+".dcm"))
        DICOMS.append(os.path.join("TempDICOM",str(count)+".dcm"))
        count+=1
    
    TextBlocks=[]
    for test in data["Test"]:
        Module = data["Test"][test]
        if type(Module) != EmptyModule:
            print("Running: "+ Module.GetModuleName())
            Module.settings["Data"] = DICOMS
            Module.settings["OutputPath"] = OutFolder

        TextBlocks.append("\n"+ Module.GetModuleName() +" Module\n")
        Module.Run()
        TextBlocks[-1] += (Module.GetReportText() +"\n")

    FileName = os.path.join(OutFolder,"Results_FromSerial_" + Seq +"_" + str(date.today())+".txt")
    MedACRAnalysisV2.WriteData(FileName,Seq,TextBlocks)

    if os.path.exists("TempDICOM"):
        shutil.rmtree("TempDICOM")
    
#RunDumpedData("/Users/john/Desktop/Results_ACR_SAG_T1_2025-10-03.12-37-10_Blair.Johnston.docx","/Users/john/Desktop/out")
