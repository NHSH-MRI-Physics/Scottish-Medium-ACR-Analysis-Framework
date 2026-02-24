from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_snr import ACRSNR
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.tasks.acr_geometric_accuracy import ACRGeometricAccuracy
from hazenlib.tasks.acr_geometric_accuracy_MagNetMethod import ACRGeometricAccuracyMagNetMethod
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
from hazenlib.tasks.acr_ghosting import ACRGhosting
from hazenlib.tasks.acr_slice_position import ACRSlicePosition
from hazenlib.tasks.acr_slice_thickness import ACRSliceThickness
from hazenlib.ACRObject import ACRObject
import pydicom
from datetime import date
from hazenlib.logger import logger
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import os 
from MedACROptions import *
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
from hazenlib._version import __version__
import PyInstallerGUI.DumpToExcel
from MedACRModules.Empty_Module import EmptyModule
import pickle
from MedACRModules.SNR_Module import SNRModule
from MedACRModules.Geo_Acc_Module import GeoAccModule
from MedACRModules.Uniformity_Module import UniformityModule
from MedACRModules.SlicePos_Module import SlicePosModule
from MedACRModules.Ghosting_Module import GhostingModule
from MedACRModules.SliceThickness_Module import SliceThicknessModule
from MedACRModules.Spatial_res_Module import SpatialResModule
import datetime
import DICOM_Holder
import MedACR_ToleranceTableCheckerV2
#from hazenlib.tasks.acr_spatial_resolution import ResOptions

#This is the upgraded version of this file which will be written in a far more modular and maintanable way.

ReportText = ""
ManualResData=None

#Default options
GeoMethod = GeometryOptions.ACRMETHOD
SpatialResMethod = ResOptions.MTFMethod
UniformityMethod = UniformityOptions.ACRMETHOD
UseLegacySliceThicknessAlgo = False
DumpToExcel = False
DICOM_Holder_Dict = None

SettingsPaneObject = None

ParamaterOverides = ParamaterOveride()

def RunAnalysisWithHolder(Holder,DICOMPath,OutputPath,RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False):
    DICOMS_Holder_Obj = DICOM_Holder_Dict[Holder]
    RunAnalysisWithData(DICOMS_Holder_Obj.paths,DICOMS_Holder_Obj.params["SeriesDescription"],OutputPath,RunAll=RunAll, RunSNR=RunSNR, RunGeoAcc=RunGeoAcc, RunSpatialRes=RunSpatialRes, RunUniformity=RunUniformity, RunGhosting=RunGhosting, RunSlicePos=RunSlicePos, RunSliceThickness=RunSliceThickness, DICOM_Params=DICOMS_Holder_Obj.params)


'''
#This is a file which simply contains a function to run the analysis. It is in a seperate file so i can reuse it for the various implementations.
def RunAnalysis(Seq,DICOMPath,OutputPath,RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False):
    files = get_dicom_files(DICOMPath)
    ACRDICOMSFiles = {}
    for file in files:
        data = pydicom.dcmread(file)
        if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
            ACRDICOMSFiles[data.SeriesDescription]=[]
        ACRDICOMSFiles[data.SeriesDescription].append(file)
    Data = ACRDICOMSFiles[Seq]
    RunAnalysisWithData(Data,Seq,OutputPath,RunAll=RunAll, RunSNR=RunSNR, RunGeoAcc=RunGeoAcc, RunSpatialRes=RunSpatialRes, RunUniformity=RunUniformity, RunGhosting=RunGhosting, RunSlicePos=RunSlicePos, RunSliceThickness=RunSliceThickness)
'''

def RunAnalysisWithData(Data,Seq,OutputPath,RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False,DICOM_Params = None):
    global ReportText
    TestsToRun= {}
    TestsToRun["SNR"] = EmptyModule("SNR")
    TestsToRun["GeoDist"] = EmptyModule("Geometric Accuracy")
    TestsToRun["SpatialRes"] = EmptyModule("Spatial Resolution")
    TestsToRun["Uniformity"] = EmptyModule("Uniformity")
    TestsToRun["Ghosting"] = EmptyModule("Ghosting")
    TestsToRun["SlicePos"] = EmptyModule("Slice Position")
    TestsToRun["SliceThickness"] = EmptyModule("Slice Thickness")

    if RunAll == True:
        RunSNR =True
        RunGeoAcc =True
        RunSpatialRes =True
        RunUniformity =True
        RunGhosting =True
        RunSlicePos =True
        RunSliceThickness =True
    settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides}
    TotalTests=0
    if RunSNR ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides}
        TestsToRun["SNR"] = SNRModule("SNR",settings)

    if RunGeoAcc ==True:
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides,"GeoMethod":GeoMethod}
        settings["GeoMethod"] = GeoMethod
        TestsToRun["GeoDist"] = GeoAccModule("Geometric Accuracy",settings)
        TotalTests+=1

    if RunSpatialRes ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides,"SpatialResMethod":SpatialResMethod, "ManualResData":ManualResData,"OutputPath":OutputPath,"Seq":Seq}
        settings["SpatialResMethod"] = SpatialResMethod
        settings["ManualResData"] = ManualResData
        settings["Seq"] = Seq
        TestsToRun["SpatialRes"] = SpatialResModule("Spatial Resolution",settings)

    if RunUniformity ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides, "UniformityMethod":UniformityMethod}
        settings["UniformityMethod"] = UniformityMethod
        TestsToRun["Uniformity"] = UniformityModule("Uniformity",settings)

    if RunGhosting ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides}
        TestsToRun["Ghosting"] = GhostingModule("Ghosting",settings)

    if RunSlicePos ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides}
        TestsToRun["SlicePos"] = SlicePosModule("Slice Position",settings)

    if RunSliceThickness ==True:
        TotalTests+=1
        #settings = {"Data":Data,"OutputPath":OutputPath,"ParamaterOverides":ParamaterOverides,"UseLegacySliceThicknessAlgo":UseLegacySliceThicknessAlgo}
        settings["UseLegacySliceThicknessAlgo"] = UseLegacySliceThicknessAlgo
        TestsToRun["SliceThickness"] = SliceThicknessModule("Slice Thickness",settings)
        

    if os.path.exists(OutputPath)==False:
        os.mkdir(OutputPath)

    FileName = os.path.join(OutputPath,"Results_" + Seq +"_" + str(date.today())+".txt")
    #ReportFile = open(FileName,"w")
    #ReportFile.write("Date Analysed: " + str(date.today()) + "\n")
    #ReportFile.write("Sequence Analysed: " + Seq + "\n")
    #ReportFile.write("Version: " + __version__)

    TestCounter=0
    TextBlocks=[]
    for test_name,module in TestsToRun.items():
        #ReportFile.write("\n"+ module.GetModuleName() +" Module\n")
        TextBlocks.append("\n"+ module.GetModuleName() +" Module\n")
        module.Run()
        #ReportFile.write(module.GetReportText() +"\n")
        TextBlocks[-1] += (module.GetReportText() +"\n")
        #ReportText+=module.GetReportText() +"\n"
        if type(module) != EmptyModule:
            TestCounter+=1
            print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    #ReportFile.close()

    WriteData(FileName,Seq,TextBlocks,DICOM_Params)
    
    ReportFile = open(FileName,"r")
    ReportText =  ''.join(ReportFile.readlines())
    ReportFile.close()
    if DumpToExcel == True:
        if os.path.exists(FileName):
            os.remove(FileName)
        PyInstallerGUI.DumpToExcel.DumpToExcel(ReportText,FileName)


    #TimeRan = datetime.datetime.now() #Perhaps this should be date of test but leave it as it is for now
    ScannerInfo = {}
    data = pydicom.dcmread(Data[0])
    acq_date = data.get("AcquisitionDate", None)   # Format: YYYYMMDD
    acq_time = data.get("AcquisitionTime", None).split(".")[0]   # Format: HHMMSS.frac, the split removes the fraction
    TimeRan = datetime.datetime.strptime(acq_date + acq_time, "%Y%m%d%H%M%S")
    ScannerInfo["Manufacturer"] = getattr(data, "Manufacturer", None) #data.Manufacturer
    ScannerInfo["Institution Name"] = getattr(data, "InstitutionName", None) #data.InstitutionName
    ScannerInfo["Model Name"] = getattr(data, "ManufacturerModelName", None) #data.ManufacturerModelName
    ScannerInfo["Serial Number"] =  getattr(data, "DeviceSerialNumber", None) #data.DeviceSerialNumber
    
    DumpData = {}
    DumpData["Test"] = TestsToRun
    DumpData["ScannerDetails"] = ScannerInfo
    DumpData["date_scanned"] = TimeRan
    DumpData["data_analysed"] = datetime.datetime.now()
    DumpData["Sequence"] = Seq
    DumpData["DICOM"] = []
    DumpData["Settings"] = settings
    DumpData["ParamaterOverides"] = ParamaterOverides   
    DumpData["ToleranceTable"] = MedACR_ToleranceTableChecker.ToleranceTable
    DumpData["SoftwareVersion"] = __version__   
    if SettingsPaneObject != None: 
        DumpData["SettingsPaneOptions"] = SettingsPaneObject.GetOptions()
    else:
        DumpData["SettingsPaneOptions"] = None
    DumpData["ResultsText"] = ReportText
    for DicomData in Data:
        DumpData["DICOM"].append(pydicom.dcmread(DicomData))

    if os.path.exists("Data_Dumps")==False:
        os.mkdir("Data_Dumps")
    
    filename = os.path.join(OutputPath,"Results_" + Seq +"_" + str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+".docx")
    with open(filename, 'wb') as f:  # open a text file
        pickle.dump(DumpData, f) # serialize the list
        
#This could be done better by making the whole thing a class, that way it only needs loaded in once. 
def GetROIFigs(Seq,DICOMPath):
    '''
    files = get_dicom_files(DICOMPath)
    ACRDICOMSFiles = {}
    for file in files:
        data = pydicom.dcmread(file)
        if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
            ACRDICOMSFiles[data.SeriesDescription]=[]
        ACRDICOMSFiles[data.SeriesDescription].append(file)
    Data = ACRDICOMSFiles[Seq]
    '''
    Data = DICOM_Holder_Dict[Seq].paths
    acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,MediumACRPhantom=True,Paramater_overide = ParamaterOverides)
    return acr_spatial_resolution_task.GetROICrops()

def WriteData(FileName,Seq, TextBlocks, DICOM_Holder_Dict):
    ReportFile = open(FileName,"w")
    ReportFile.write("Date Analysed: " + str(date.today()) + "\n")
    ReportFile.write("Sequence Analysed: " + Seq + "\n")
    ReportFile.write("Version: " + __version__  + "\n")
    ReportFile.write("TE: " + str(DICOM_Holder_Dict["EchoTime"]) + " ms\n")
    ReportFile.write("TR: " + str(DICOM_Holder_Dict["RepetitionTime"]) + " ms\n")
    ReportFile.write("BW: " + str(DICOM_Holder_Dict["Bandwidth"]) + " Hz\n")
    for block in TextBlocks:
        ReportFile.write(block)

    OverrideText = ""
    if ParamaterOverides.CentreOverride != None:
        OverrideText += "Center Override Position: " + str(ParamaterOverides.CentreOverride[0]) + "," + str(ParamaterOverides.CentreOverride[1]) + "\n"
    if ParamaterOverides.RadiusOverride != None:
        OverrideText += "Radius Override: " + str(ParamaterOverides.RadiusOverride) + "\n" 

    MaskingOverride = False
    for slice in ParamaterOverides.MaskingOverride:
        if slice.any() != None:
            MaskingOverride = True
    #if len(np.where(ParamaterOverides.MaskingOverride!=None)[0]) != 0:
    if MaskingOverride == True: 
        OverrideText += "Making Override: True\n"


    if ParamaterOverides.ROIOverride != None:
        OverrideText += "ROI Position Override: True\n"
    
    if OverrideText != "":
        ReportFile.write("\nOverrides Active\n")
        ReportFile.write(OverrideText)
    ReportFile.close()