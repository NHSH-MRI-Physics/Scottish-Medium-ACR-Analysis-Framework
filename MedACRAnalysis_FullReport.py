from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_snr import ACRSNR
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.tasks.acr_geometric_accuracy import ACRGeometricAccuracy
from hazenlib.tasks.acr_geometric_accuracy2 import ACRGeometricAccuracy2
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

#This is a file which simply contains a function to run the analysis. It is in a seperate file so i can reuse it for the various implementations.
def RunAnalysis(Seq,DICOMPath,OutputPath,RunAll=True, RunSNR=False, RunGeoAccEdges=False, RunGeoAccRods=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False):
    if RunAll == True:
        TotalTests = 7
    else:
        TotalTests=0
        if RunSNR ==True:
            TotalTests+=1
        if RunGeoAccEdges ==True:
            TotalTests+=1
        if RunGeoAccRods ==True:
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

    ToleranceTable = {}
    ToleranceTable["SNR"]=[None,None]
    ToleranceTable["Geometric Acuracy"]=[None,None]
    ToleranceTable["Uniformity"]=[None,None]
    ToleranceTable["Ghosting"]=[None,None]
    ToleranceTable["Slice Position"]=[None,None]
    ToleranceTable["Slice Thickness"]=[None,None]
    ToleranceTable["Spatial Resolution 1.1mm"]=[None,None]
    ToleranceTable["Spatial Resolution 1.0mm"]=[None,None]
    ToleranceTable["Spatial Resolution 0.9mm"]=[None,None]
    ToleranceTable["Spatial Resolution 0.8mm"]=[None,None]
    ToleranceTable["Spatial Resolution MTF50 Raw"]=[None,None]
    ToleranceTable["Spatial Resolution MTF50 Fitted"]=[None,None]

    f = open("ToleranceTable/ToleranceTable.txt")
    for line in f: 
        if line[0]!="#":
            Name = line.split(",")[0].strip()
            Lower = line.split(",")[1].strip()
            Upper = line.split(",")[2].strip()
            if Lower == "None" or Lower=="none":
                Lower = None
            else:
                Lower=float(Lower)
            if Upper == "None" or Upper=="none":
                Upper = None
            else:
                Upper=float(Upper)
            if Name not in ToleranceTable.keys():
                logger.error("Unknown test name in the tolerance table")
            ToleranceTable[Name] = [Lower,Upper]


    if os.path.exists(OutputPath)==False:
        os.mkdir(OutputPath)
    FileName = os.path.join(OutputPath,"Results_" + Seq +"_" + str(date.today())+".txt")
    ReportFile = open(FileName,"w")

    ReportFile.write("Date Analysed: " + str(date.today()) + "\n")
    ReportFile.write("Sequence Analysed: " + Seq + "\n")


    def GetPassResult(Value,TestName):
        if ToleranceTable[TestName]==[None,None]:
            return "Result: No Tolerance Set"
        Pass=True
        Appendix = []
        if ToleranceTable[TestName][1]!=None:
            if Value > ToleranceTable[TestName][1]:
                Pass=False
            Appendix.append("<"+str(ToleranceTable[TestName][1]))
        if ToleranceTable[TestName][0]!=None:
            if Value < ToleranceTable[TestName][0]:
                Pass=False
            Appendix.append(">"+str(ToleranceTable[TestName][0]))
        AppendixTxt=""
        if len(Appendix) == 1 :
            AppendixTxt = Appendix[0]
        if len(Appendix) == 2 :
            AppendixTxt = Appendix[1] +" and " + Appendix[0]

        if Pass ==True:
            return ("Result: Pass      Tolerance: " + AppendixTxt)
        else:
            return ("Result: Fail      Tolerance: " + AppendixTxt) 
        
    TestCounter=0
    ReportFile.write("\nSNR Module\n")
    if RunAll==True or RunSNR == True:
        print("Running SNR")
        acr_snr_task = ACRSNR(input_data=Data, report_dir=OutputPath,report=True,MediumACRPhantom=True)
        snr = acr_snr_task.run()
        print("SNR :" +str(snr["measurement"]["snr by smoothing"]["measured"]))
        print("Normalised SNR :" +str(snr["measurement"]["snr by smoothing"]["normalised"]))
        
        ReportFile.write( '\tSNR: %-12s%-12s\n' % (str(snr["measurement"]["snr by smoothing"]["measured"]), GetPassResult(snr["measurement"]["snr by smoothing"]["measured"],"SNR")))
        ReportFile.write( '\tNormalised SNR: %-12s%-12s\n' % (str(snr["measurement"]["snr by smoothing"]["normalised"]), GetPassResult(snr["measurement"]["snr by smoothing"]["normalised"],"SNR")))
        ReportFile.write( '\tCentre of phantom at (x,,y): %-12s%-12s\n' % (str(snr["measurement"]["snr by smoothing"]["centre x"]), str(snr["measurement"]["snr by smoothing"]["centre y"])))        
        ReportFile.write( '\tSignal(Means of image ROIs): Centre=%-6s' % str(snr["measurement"]["snr by smoothing"]["signal"][0]))
        ReportFile.write(', BL= %-6s ' % (str(snr["measurement"]["snr by smoothing"]["signal"][1])))
        ReportFile.write(', LR= %-6s ' % (str(snr["measurement"]["snr by smoothing"]["signal"][2])))
        ReportFile.write(', UL= %-6s ' % (str(snr["measurement"]["snr by smoothing"]["signal"][3])))
        ReportFile.write(', UR= %-6s' % (str(snr["measurement"]["snr by smoothing"]["signal"][4])))
        ReportFile.write( '\n\tNoise(StDev of subtracted-image ROIs): Centre=%-4s' % str(snr["measurement"]["snr by smoothing"]["noise"][0]))
        ReportFile.write(', BL= %-4s ' % (str(snr["measurement"]["snr by smoothing"]["noise"][1])))
        ReportFile.write(', LR= %-4s ' % (str(snr["measurement"]["snr by smoothing"]["noise"][2])))
        ReportFile.write(', UL= %-4s ' % (str(snr["measurement"]["snr by smoothing"]["noise"][3])))
        ReportFile.write(', UR= %-4s' % (str(snr["measurement"]["snr by smoothing"]["noise"][4])))                        
        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nGeometric Accuracy Module(Edges)\n")
    if RunAll==True or RunGeoAccEdges == True:
        print("Running Geometric Accuracy(Edges)")
        acr_geometric_accuracy_task = ACRGeometricAccuracy(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
        GeoDist = acr_geometric_accuracy_task.run()
        print("Slice 1 Hor Dist: "+str(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"]) + "   "+ " Vert Dist: "+str(GeoDist["measurement"][GeoDist["file"][0]]["Vertical distance"]))
        print("Slice 5 Hor Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"]) + "   "+ " Vert Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Vertical distance"])+ "   "+ " Diag SW Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"])+ "   "+ "Diag SE Dist:"+str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"]))
        
        
        ReportFile.write("\tSlice 1:\n")
        ReportFile.write( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"],"Geometric Acuracy") ))
        ReportFile.write( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][0]]["Vertical distance"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][0]]["Horizontal distance"],"Geometric Acuracy") ))

        ReportFile.write("\tSlice 5:\n")
        ReportFile.write( '\t\tHor Dist (mm):             %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"],"Geometric Acuracy") ))
        ReportFile.write( '\t\tVert Dist (mm):            %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Vertical distance"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Horizontal distance"],"Geometric Acuracy") ))
        ReportFile.write( '\t\tDiagonal distance SW (mm): %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SW"],"Geometric Acuracy") ))
        ReportFile.write( '\t\tDiagonal distance SE (mm): %-12s%-12s\n' % (str(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"]),GetPassResult(GeoDist["measurement"][GeoDist["file"][1]]["Diagonal distance SE"],"Geometric Acuracy") ))
        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nGeometric Accuracy Module(Rods)\n")
    if RunAll==True or RunGeoAccRods == True:
        print("Running Geometric Accuracy(Rods)")
        acr_geometric_accuracy_task = ACRGeometricAccuracy2(input_data=Data,report_dir=OutputPath,MediumACRPhantom=True,report=True)
        GeoDist = acr_geometric_accuracy_task.run()
        print("Horizontal CoV(%) = "+str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal mm"]))
        print("Vertical CoV(%) = "+str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical mm"]))
 #       print("Row Top: "+str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0]) + "   "+ 
 #           "Row Middle: "+str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1]) + "  "+ 
 #           "Row bottom: "+str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2]))

#        ReportFile.write( '\tHorizontal CoV (%):%-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal mm"]) ))
#        ReportFile.write( '\t\tVertical CoV (%):   %-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical mm"])))
        ReportFile.write( '\t\tHorizontal CoV:     %-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["horizontal mm"])))
        ReportFile.write( '\t\tVertical CoV:       %-12s\n' % (str(GeoDist["measurement"]["distortion"]["distortion values"]["vertical mm"])))
        ReportFile.write( '\t\tRow Top (mm):       %-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][0])))
        ReportFile.write( '\t\tRow Middle (mm):    %-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][1])))
        ReportFile.write( '\t\tRow Bottom (mm):    %-12s\n' % (str(GeoDist["measurement"]["distortion"]["horizontal distances mm"][2])))
        ReportFile.write( '\t\tCol Top (mm):       %-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][0])))
        ReportFile.write( '\t\tCol Middle (mm):    %-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][1])))
        ReportFile.write( '\t\tCol Bottom (mm):    %-12s\n' % (str(GeoDist["measurement"]["distortion"]["vertical distances mm"][2])))
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.write("\nSpatial Resoloution Module\n")
    if RunAll==True or RunSpatialRes == True:
        print("Running Spatial Resoloution")
        #Run the dot matrix version
        acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,UseDotMatrix=True)
        Res = acr_spatial_resolution_task.run()

        ReportFile.write( '\t1.1mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.1mm holes"]),GetPassResult(Res["measurement"]["1.1mm holes"],"Spatial Resolution 1.1mm") ))
        ReportFile.write( '\t1.0mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["1.0mm holes"]),GetPassResult(Res["measurement"]["1.0mm holes"],"Spatial Resolution 1.0mm") ))
        ReportFile.write( '\t0.9mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.9mm holes"]),GetPassResult(Res["measurement"]["0.9mm holes"],"Spatial Resolution 0.9mm") ))
        ReportFile.write( '\t0.8mm Holes Score: %-12s%-12s\n' % (str(Res["measurement"]["0.8mm holes"]),GetPassResult(Res["measurement"]["0.8mm holes"],"Spatial Resolution 0.8mm") ))
        
        #Run the MTF
        acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,UseDotMatrix=False)
        Res = acr_spatial_resolution_task.run()
        ReportFile.write( '\tRaw MTF50 :        %-12s%-12s\n' % (str(Res["measurement"]["raw mtf50"]),GetPassResult(Res["measurement"]["raw mtf50"],"Spatial Resolution MTF50 Raw") ))
        ReportFile.write( '\tFitted MTF50:      %-12s%-12s\n' % (str(Res["measurement"]["fitted mtf50"]),GetPassResult(Res["measurement"]["fitted mtf50"],"Spatial Resolution MTF50 Fitted") ))

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
        ReportFile.write( '\tUniformity:  %-12s%-12s\n' % (str(UniformityResult["measurement"]["integral uniformity %"])+"%",GetPassResult(UniformityResult["measurement"]["integral uniformity %"],"Uniformity") ))
        ReportFile.write( '\tMean of the Max ROI:  %-6s\n' % (str(UniformityResult["measurement"]["max roi"])))
        ReportFile.write( '\tMean of the Min ROI:  %-6s\n' % (str(UniformityResult["measurement"]["min roi"])))
        ReportFile.write( '\tPosition of the Max ROI:  %-6s\n' % (str(UniformityResult["measurement"]["max pos"])))
        ReportFile.write( '\tPosition of the Min ROI:  %-6s\n' % (str(UniformityResult["measurement"]["min pos"])))
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

        ReportFile.write( '\tGhosting:    %-12s%-12s\n' % (str(ghosting["measurement"]["signal ghosting %"])+"%",GetPassResult(ghosting["measurement"]["signal ghosting %"],"Ghosting") ))
        ReportFile.write( '\t\tMean ROI(Large Phantom):  %-12s\n' % (str(ghosting["measurement"]["large roi"])))
        ReportFile.write( '\t\tMean ROI(Bkg Top):        %-12s\n' % (str(ghosting["measurement"]["n roi"])))
        ReportFile.write( '\t\tMean ROI(Bkg Bottom):     %-12s\n' % (str(ghosting["measurement"]["s roi"])))
        ReportFile.write( '\t\tMean ROI(Bkg Left):       %-12s\n' % (str(ghosting["measurement"]["e roi"])))
        ReportFile.write( '\t\tMean ROI(Bkg Right):      %-12s\n' % (str(ghosting["measurement"]["w roi"])))
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

        ReportFile.write( '\tSlice 1 Position Error (mm):  %-12s%-12s\n' % (str(SlicePos['measurement'][SlicePos['file'][0]]['length difference']),GetPassResult(SlicePos['measurement'][SlicePos['file'][0]]['length difference'],"Slice Position") ))
        ReportFile.write( '\tSlice 11 Position Error (mm): %-12s%-12s\n' % (str(SlicePos['measurement'][SlicePos['file'][1]]['length difference']),GetPassResult(SlicePos['measurement'][SlicePos['file'][1]]['length difference'],"Slice Position") ))

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
        #ReportFile.write("\tSlice Width (mm): " + str(SliceThick['measurement']['slice width mm'])+"\t" + GetPassResult(SliceThick['measurement']['slice width mm'],"Slice Thickness") +"\n")
        ReportFile.write( '\tSlice Width (mm): %-12s%-12s\n' % (str(SliceThick['measurement']['slice width mm']),GetPassResult(SliceThick['measurement']['slice width mm'],"Slice Thickness") ))

        TestCounter+=1
        print("Progress " +str(TestCounter) +"/" +str(TotalTests))
    else:
        ReportFile.write("\tNot Run\n")

    ReportFile.close()