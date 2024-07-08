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

ReportText = ""
ManualResTestText=None

#Default options
GeoMethod = GeometryOptions.ACRMETHOD

#This is a file which simply contains a function to run the analysis. It is in a seperate file so i can reuse it for the various implementations.
def RunAnalysis(Seq,DICOMPath,OutputPath,RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False):
    global ReportText
    
    if RunAll == True:
        TotalTests = 7
    else:
        TotalTests=0
        if RunSNR ==True:
            TotalTests+=1
        if RunGeoAcc ==True:
            TotalTests+=1
        if RunSpatialRes ==True:
            TotalTests+=1
        if RunUniformity ==True:
            TotalTests+=1
        if RunGhosting ==True:
            TotalTests+=1
        if RunSlicePos ==True:
            TotalTests+=1
        if RunSliceThickness ==True:
            TotalTests+=1
            
    #load in the DICOM
    #DICOMPath="DataTransfer"

    files = get_dicom_files(DICOMPath)
    ACRDICOMSFiles = {}
    for file in files:
        data = pydicom.dcmread(file)
        if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
            ACRDICOMSFiles[data.SeriesDescription]=[]
        ACRDICOMSFiles[data.SeriesDescription].append(file)
    Data = ACRDICOMSFiles[Seq]

        

    if os.path.exists(OutputPath)==False:
        os.mkdir(OutputPath)
    FileName = os.path.join(OutputPath,"Results_" + Seq +"_" + str(date.today())+".txt")
    ReportFile = open(FileName,"w")

    ReportFile.write("Date Analysed: " + str(date.today()) + "\n")
    ReportFile.write("Sequence Analysed: " + Seq + "\n")

    TestCounter=0
    ReportFile.write("\nSNR Module\n")
    if RunAll==True or RunSNR == True:
        print("Running SNR")
        acr_snr_task = ACRSNR(input_data=Data, report_dir=OutputPath,report=True,MediumACRPhantom=True)
        snr = acr_snr_task.run()
        print("SNR :" +str(snr["measurement"]["snr by smoothing"]["measured"]))
        print("Normalised SNR :" +str(snr["measurement"]["snr by smoothing"]["normalised"]))
        
        ReportFile.write( '\tSNR:            %-12s%-12s\n' % (str(snr["measurement"]["snr by smoothing"]["measured"]), MedACR_ToleranceTableChecker.GetPassResult(snr["measurement"]["snr by smoothing"]["measured"],"SNR")))
        ReportFile.write( '\tNormalised SNR: %-12s%-12s\n' % (str(snr["measurement"]["snr by smoothing"]["normalised"]), MedACR_ToleranceTableChecker.GetPassResult(snr["measurement"]["snr by smoothing"]["normalised"],"SNR")))
        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nGeometric Accuracy Module\n")

    if RunAll==True or RunGeoAcc == True:
        print("Running Geometric Accuracy")

        if (GeoMethod == GeometryOptions.ACRMETHOD):
            acr_geometric_accuracy_task = ACRGeometricAccuracy(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
            GeoDist = acr_geometric_accuracy_task.run()
            print("Slice 1 Hor Dist: "+str(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"]) + "   "+ " Vert Dist: "+str(GeoDist["measurement"][GeoDist["file"][0]]["Vertical distance"]))
            print("Slice 5 Hor Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"]) + "   "+ " Vert Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Vertical distance"])+ "   "+ " Diag SW Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"])+ "   "+ "Diag SE Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"]))
            ReportFile.write("\tSlice 1:\n")
            ReportFile.write( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            ReportFile.write( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][0]]["Vertical distance"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][0]]["Vertical distance"],"Geometric Accuracy","ACRMethod") ))

            ReportFile.write("\tSlice 5:\n")
            ReportFile.write( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            ReportFile.write( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Vertical distance"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"],"Geometric Accuracy","ACRMethod") ))
            ReportFile.write( '\t\tDiagonal distance SW (mm): %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"],"Geometric Accuracy","ACRMethod") ))
            ReportFile.write( '\t\tDiagonal distance SE (mm): %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"],"Geometric Accuracy","ACRMethod") ))
        if (GeoMethod == GeometryOptions.MAGNETMETHOD):
            acr_geometric_accuracy_MagNetMethod = ACRGeometricAccuracyMagNetMethod(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
            GeoDist = acr_geometric_accuracy_MagNetMethod.run()
            print("Horizontal CoV(%):        "+str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"]))
            print("Vertical CoV(%):          "+str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"]))
                
            ReportFile.write( '\t\tHorizontal CoV:     %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"],"Geometric Accuracy")))
            ReportFile.write( '\t\tVertical CoV:       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Top (mm):       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Middle (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Bottom (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Top (mm):       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][0],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Middle (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][1],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Bottom (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][2],"Geometric Accuracy")))        

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nSpatial Resoloution Module\n")
    if RunAll==True or RunSpatialRes == True:
        print("Running Spatial Resoloution")
        #Run the dot matrix version
        acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,UseDotMatrix=True)
        Res = acr_spatial_resolution_task.run()

        ReportFile.write( '\t1.1mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.1mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.1mm holes"],"Spatial Resolution 1.1mm") ))
        ReportFile.write( '\t1.0mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.0mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.0mm holes"],"Spatial Resolution 1.0mm") ))
        ReportFile.write( '\t0.9mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.9mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.9mm holes"],"Spatial Resolution 0.9mm") ))
        ReportFile.write( '\t0.8mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.8mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.8mm holes"],"Spatial Resolution 0.8mm") ))
        
        #Run the MTF
        acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,UseDotMatrix=False)
        Res = acr_spatial_resolution_task.run()
        ReportFile.write( '\tRaw MTF50 :        %-12s%-12s\n' % (str(Res["measurement"]["raw mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["raw mtf50"],"Spatial Resolution MTF50 Raw") ))
        ReportFile.write( '\tFitted MTF50:      %-12s%-12s\n' % (str(Res["measurement"]["fitted mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["fitted mtf50"],"Spatial Resolution MTF50 Fitted") ))

        #Add in Manual Res Test
        if ManualResTestText != None:
            for key in ManualResTestText:
                Result = "Not Tested"
                if ManualResTestText[key]==True:
                    Result="Resolved"
                elif ManualResTestText[key]==False:
                    Result="Not Resolved"
                
                ReportFile.write( '\tManual '+key+' Resolution : %-15s%-12s\n' % (str(Result),MedACR_ToleranceTableChecker.GetPassResult(Result,"Manual Resolution",key)))
        TestCounter+=1


        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nUniformity Module\n")
    if RunAll==True or RunUniformity == True:
        print("Running Uniformity")
        acr_uniformity_task = ACRUniformity(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
        UniformityResult=acr_uniformity_task.run()
        print(" Uniformity :" + str(UniformityResult["measurement"]["integral uniformity %"]))
        ReportFile.write( '\tUniformity:  %-12s%-12s\n' % (str(UniformityResult["measurement"]["integral uniformity %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(UniformityResult["measurement"]["integral uniformity %"],"Uniformity") ))
        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nGhosting Module\n")
    if RunAll==True or RunGhosting == True:
        print("Running Ghosting")
        acr_ghosting_task = ACRGhosting(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
        ghosting = acr_ghosting_task.run()
        print("Ghosting :" + str(ghosting["measurement"]["signal ghosting %"]))

        ReportFile.write( '\tGhosting:    %-12s%-12s\n' % (str(ghosting["measurement"]["signal ghosting %"])+"%",MedACR_ToleranceTableChecker.GetPassResult(ghosting["measurement"]["signal ghosting %"],"Ghosting") ))

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nSlice Position Module\n")
    if RunAll==True or RunSlicePos == True:
        print("Running Slice Position")
        acr_slice_position_task = ACRSlicePosition(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True)
        SlicePos = acr_slice_position_task.run()
        print("Slice Pos difference " + SlicePos['file'][0] + " :" + str(SlicePos['measurement'][SlicePos['file'][0]]['length difference']) + "mm    " + SlicePos['file'][1] + " :" + str(SlicePos['measurement'][SlicePos['file'][1]]['length difference'])+"mm")

        ReportFile.write( '\tSlice 1 Position Error (mm):  %-12s%-12s\n' % (str(SlicePos['measurement'][SlicePos['file'][0]]['length difference']),MedACR_ToleranceTableChecker.GetPassResult(SlicePos['measurement'][SlicePos['file'][0]]['length difference'],"Slice Position") ))
        ReportFile.write( '\tSlice 11 Position Error (mm): %-12s%-12s\n' % (str(SlicePos['measurement'][SlicePos['file'][1]]['length difference']),MedACR_ToleranceTableChecker.GetPassResult(SlicePos['measurement'][SlicePos['file'][1]]['length difference'],"Slice Position") ))

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nSlice Thickness Module\n")
    if RunAll==True or RunSliceThickness == True:
        print("Running Slice Thickness")
        acr_slice_thickness_task = ACRSliceThickness(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True)
        SliceThick = acr_slice_thickness_task.run()
        print("Slice Width (mm): " + str(SliceThick['measurement']['slice width mm']))
        #ReportFile.write("\tSlice Width (mm): " + str(SliceThick['measurement']['slice width mm'])+"\t" + MedACR_ToleranceTableChecker.GetPassResult(SliceThick['measurement']['slice width mm'],"Slice Thickness") +"\n")
        ReportFile.write( '\tSlice Width (mm): %-12s%-12s\n' % (str(SliceThick['measurement']['slice width mm']),MedACR_ToleranceTableChecker.GetPassResult(SliceThick['measurement']['slice width mm'],"Slice Thickness") ))

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")
    ReportFile.close()

    ReportFile = open(FileName,"r")
    ReportText =  ''.join(ReportFile.readlines())
    ReportFile.close()


#This could be done better by making the whole thing a class, that way it only needs loaded in once. 
def GetROIFigs(Seq,DICOMPath):
    files = get_dicom_files(DICOMPath)
    ACRDICOMSFiles = {}
    for file in files:
        data = pydicom.dcmread(file)
        if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
            ACRDICOMSFiles[data.SeriesDescription]=[]
        ACRDICOMSFiles[data.SeriesDescription].append(file)
    Data = ACRDICOMSFiles[Seq]
    acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,MediumACRPhantom=True)
    return acr_spatial_resolution_task.GetROICrops()