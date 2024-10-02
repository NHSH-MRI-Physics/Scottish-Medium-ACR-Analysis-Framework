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
#from hazenlib.tasks.acr_spatial_resolution import ResOptions

ReportText = ""
ManualResData=None

#Default options
GeoMethod = GeometryOptions.ACRMETHOD
SpatialResMethod = ResOptions.MTFMethod


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
            acr_geometric_accuracy_MagNetMethod = ACRGeometricAccuracyMagNetMethod(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True, SkipGaussFit=True)
            GeoDist = acr_geometric_accuracy_MagNetMethod.run()
            print("Horizontal CoV(%):        "+str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"]))
            print("Vertical CoV(%):          "+str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"]))
                
            ReportFile.write( '\t\tHorizontal CoV:     %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal CoV"],"Geometric Accuracy")))
            ReportFile.write( '\t\tVertical CoV:       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["distortion values"]["vertical CoV"],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Bottom (mm):       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Middle (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1],"Geometric Accuracy")))
            ReportFile.write( '\t\tRow Top (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Left (mm):       %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][0]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][0],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Middle (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][1]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][1],"Geometric Accuracy")))
            ReportFile.write( '\t\tCol Right (mm):    %-12s%-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][2]),MedACR_ToleranceTableChecker.GetPassResult(GeoDist["measurement"]["distortion"]["vertical distances mm"][2],"Geometric Accuracy")))        

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nSpatial Resoloution Module\n")
    if RunAll==True or RunSpatialRes == True:
        print("Running Spatial Resoloution")
        #Run the dot matrix version
        if SpatialResMethod != ResOptions.Manual:
            acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True)
            acr_spatial_resolution_task.ResOption=SpatialResMethod
            Res = acr_spatial_resolution_task.run()

        if SpatialResMethod == ResOptions.DotMatrixMethod:
            ReportFile.write( '\t1.1mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.1mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.1mm holes"],"Spatial Resolution 1.1mm") ))
            ReportFile.write( '\t1.0mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.0mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.0mm holes"],"Spatial Resolution 1.0mm") ))
            ReportFile.write( '\t0.9mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.9mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.9mm holes"],"Spatial Resolution 0.9mm") ))
            ReportFile.write( '\t0.8mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.8mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.8mm holes"],"Spatial Resolution 0.8mm") ))
            
        elif SpatialResMethod == ResOptions.MTFMethod:
            #Run the MTF
            ReportFile.write( '\tRaw MTF50 :        %-12s%-12s\n' % (str(Res["measurement"]["raw mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["raw mtf50"],"Spatial Resolution MTF50 Raw") ))
            ReportFile.write( '\tFitted MTF50:      %-12s%-12s\n' % (str(Res["measurement"]["fitted mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["fitted mtf50"],"Spatial Resolution MTF50 Fitted") ))

        elif SpatialResMethod == ResOptions.ContrastResponseMethod:
            ReportFile.write( '\tHorizontal Contrast Response\n')
            ReportFile.write( '\t\t1.1mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["1.1mm holes Horizontal"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.1mm holes Horizontal"],"Contrast Response Resolution","1.1mm holes Horizontal")))
            ReportFile.write( '\t\t1.0mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["1.0mm holes Horizontal"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.0mm holes Horizontal"],"Contrast Response Resolution","1.0mm holes Horizontal")))
            ReportFile.write( '\t\t0.9mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["0.9mm holes Horizontal"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.9mm holes Horizontal"],"Contrast Response Resolution","0.9mm holes Horizontal")))
            ReportFile.write( '\t\t0.8mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["0.8mm holes Horizontal"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.8mm holes Horizontal"],"Contrast Response Resolution","0.8mm holes Horizontal")))

            ReportFile.write( '\tVertical Contrast Response\n')
            ReportFile.write( '\t\t1.1mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["1.1mm holes Vertical"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.1mm holes Vertical"],"Contrast Response Resolution","1.1mm holes Vertical")))
            ReportFile.write( '\t\t1.0mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["1.0mm holes Vertical"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["1.0mm holes Vertical"],"Contrast Response Resolution","1.0mm holes Vertical")))
            ReportFile.write( '\t\t0.9mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["0.9mm holes Vertical"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.9mm holes Vertical"],"Contrast Response Resolution","0.9mm holes Vertical")))
            ReportFile.write( '\t\t0.8mm Contrast Response: %-12s%-12s\n' % (str(Res["measurement"]["0.8mm holes Vertical"]),MedACR_ToleranceTableChecker.GetPassResult(Res["measurement"]["0.8mm holes Vertical"],"Contrast Response Resolution","0.8mm holes Vertical")))
        elif SpatialResMethod == ResOptions.Manual:
            pass
        else:
            raise Exception("Unexpected option in spatial res module")

        #Add in Manual Res Test
        if ManualResData != None:
            for key in ManualResData:
                Result = "Not Tested"
                import matplotlib
                matplotlib.use( 'tkagg' )
                fig, (ax1, ax2, ax3) = plt.subplots(3,1)
                fig.suptitle(key + ' Manual Resolution Output',y=0.99)
                fig.set_size_inches(20, 20)
                ax1.imshow(ManualResData[key].Image)
                ContrastResponse = []
                for Direction in range(2):                    
                    xpointsPeaks = ManualResData[key].ChosenPointsXPeaks[Direction]
                    ypointsPeaks = ManualResData[key].ChosenPointsYPeaks[Direction]
                    xpointsTroughs = ManualResData[key].ChosenPointsXTroughs[Direction]
                    ypointsTroughs = ManualResData[key].ChosenPointsYTroughs[Direction]

                    #Do Peaks
                    zPeaks = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((ypointsPeaks,xpointsPeaks)),order=1, mode = "nearest")

                    xLine = np.array([])
                    yLine = np.array([])                    
                    for i in range(3):
                        endpoint = False
                        if i == 2:
                            endpoint=True
                        xLine=np.append(xLine, np.linspace(xpointsPeaks[i],xpointsTroughs[i],endpoint=False))
                        xLine=np.append(xLine, np.linspace(xpointsTroughs[i],xpointsPeaks[i+1],endpoint=endpoint))

                        yLine=np.append(yLine, np.linspace(ypointsPeaks[i],ypointsTroughs[i],endpoint=False))
                        yLine=np.append(yLine, np.linspace(ypointsTroughs[i],ypointsPeaks[i+1],endpoint=endpoint))
                    zLine = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((yLine,xLine)),order=1, mode = "nearest")
           
                    MeanPeak = np.mean(zPeaks)
                    if Direction==0:
                        ax1.plot(xpointsPeaks, ypointsPeaks,marker="X",ls='',color="blue",markersize=10)
                    else:
                        ax1.plot(xpointsPeaks, ypointsPeaks,marker="X",ls='',color="red",markersize=10)

                    if Direction==0: 
                        ax2.plot(xpointsPeaks,zPeaks, marker="X",ls='',color="blue",markersize=10,label ="Horizontal Peaks")  
                        ax2.axhline(y=MeanPeak, color='blue', linestyle='-',label ="Mean Peak")
                        ax2.plot(xLine, zLine,marker="",ls='-.',color="blue",label="Sample Line")
                    else:
                        ax3.plot(ypointsPeaks,zPeaks, marker="X",ls='',color="red",markersize=10,label ="Vertical Peaks")   
                        ax3.axhline(y=MeanPeak, color='red', linestyle='-',label ="Mean Peak")      
                        ax3.plot(yLine, zLine,marker="",ls='-.',color="red",label="Sample Line") 

                    #Do Troughs
                    zTroughs = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((ypointsTroughs,xpointsTroughs)),order=1, mode = "nearest")
                    MeanTrough = np.mean(zTroughs)
                    if Direction==0:
                        ax1.plot(xpointsTroughs, ypointsTroughs,marker="o",ls='',color="blue",markersize=10)
                    else:
                        ax1.plot(xpointsTroughs, ypointsTroughs,marker="o",ls='',color="red",markersize=10)
            
                    if Direction==0: 
                        ax2.plot(xpointsTroughs,zTroughs, marker="o",ls='',color="blue",markersize=10,label ="Horizontal Troughs")     
                        ax2.axhline(y=MeanTrough, color='blue', linestyle='--',label ="Mean Trough")
                        ax2.legend()
                    else:       
                        ax3.plot(ypointsTroughs,zTroughs, marker="o",ls='',color="red",markersize=10,label ="Vertical Troughs")   
                        ax3.axhline(y=MeanTrough, color='red', linestyle='--',label ="Mean Trough")
                        ax3.legend()
                    
                    
                    Amplitude = abs(MeanPeak - MeanTrough)
                    ContrastResponse.append(round(Amplitude/MeanPeak,3))
                
                fig.tight_layout()
                if not os.path.exists(OutputPath+"/ACRSpatialResolution"):
                    os.makedirs(OutputPath+"/ACRSpatialResolution")
                plt.savefig(OutputPath+"/ACRSpatialResolution/"+Seq+"_"+key+"_ManualRes.png")
                plt.close()
                #plt.show()

                ReportFile.write( '\tManual '+key+' Resolution Hor: %-15s%-12s\n' % (str(ContrastResponse[0]),MedACR_ToleranceTableChecker.GetPassResult(ContrastResponse[0],"Manual Resolution",key +" Horizontal")))
                ReportFile.write( '\tManual '+key+' Resolution Vert: %-15s%-12s\n' % (str(ContrastResponse[1]),MedACR_ToleranceTableChecker.GetPassResult(ContrastResponse[1],"Manual Resolution",key +" Vertical")))
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