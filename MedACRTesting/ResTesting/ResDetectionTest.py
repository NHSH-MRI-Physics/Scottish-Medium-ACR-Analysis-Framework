import sys
sys.path.append(".")
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import filters
from hazenlib.utils import get_dicom_files
import pydicom
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
import math
import matplotlib.patches as patches
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import scipy.signal
import matplotlib.gridspec as gridspec
from scipy.optimize import curve_fit
from scipy.interpolate import griddata


inputdata = "MedACRTesting/TestData/ACR_ARDL_Tests"
Seq = "ACR AxT1 High Res"
#Seq = "ACR AxT1"
files = get_dicom_files(inputdata)
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
Data = ACRDICOMSFiles[Seq]

acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir="OutputFolder",report=True,MediumACRPhantom=True,UseDotMatrix=True)
Crops = acr_spatial_resolution_task.GetROICrops()
res = acr_spatial_resolution_task.ACR_obj.pixel_spacing[0]
imgs = [Crops["1.1mm holes"],Crops["1.0mm holes"],Crops["0.9mm holes"],Crops["0.8mm holes"]]
HoleSize = [1.1,1.0,0.9,0.8]

fig = plt.figure(figsize=(15, 10))
gs = gridspec.GridSpec(nrows=4, ncols=4,height_ratios=[3, 1,1,1])
gridspec_kw={'width_ratios': [1, 3]}
def GetContrastResponseFactor(Lines,PixelSteps,CurrentHole):
    #All this below should be in a fuunction
    Peaks, PeakProperties = scipy.signal.find_peaks(Lines,distance=PixelSteps)
    Troughs, TroughsProperties = scipy.signal.find_peaks(-Lines,distance=PixelSteps)
    
    #plt.close("all")
    #plt.plot(Lines)
    #plt.show()

    #Peaks=list(np.delete(Peaks,[1]))
    #Troughs=list(np.delete(Troughs,[1]))

    PeaksandTroughs = list(Peaks)+list(Troughs)        
    
    def Sin(x, phase):
        return np.sin(2*np.pi*x * 1/(PixelSteps*2) + phase) * np.max(Lines)/2 + np.mean(Lines)
    p0=[0]
    fit = curve_fit(Sin, PeaksandTroughs, Lines[PeaksandTroughs], p0=p0)
    x=np.arange(0,xCutoff,0.0001)
    data_fit = Sin(x,*fit[0])

    PreicatedPeaks=[]
    PreicatedTroughs=[]
    for i in range (0,4):
        PreicatedPeaks.append (((np.pi/2+i*2*np.pi) - fit[0][0] )/(2*np.pi*(1/(PixelSteps*2))))
        PreicatedTroughs.append (((3*np.pi/2+i*2*np.pi) - fit[0][0] )/(2*np.pi*(1/(PixelSteps*2))))

    #Organise the peaks to check for any gaps or false peaks
    PeakOrgArray = [None,None,None,None]
    for peak in Peaks:
        diff = np.abs(np.array(PreicatedPeaks)-peak)
        Idx = np.argmin(diff)
        if PeakOrgArray[Idx]==None:
            PeakOrgArray[Idx] = peak
        else:
            if diff[Idx] < PeakOrgArray[Idx]: #If two peaks get slotted into the same region then take the one that best matches the expected position. 
                PeakOrgArray[Idx] = peak

    FinalPeaks = [None,None,None,None]
    for OrgIdx in range(0,len(PeakOrgArray)):
        if PeakOrgArray[OrgIdx]!=None:
            FinalPeaks[OrgIdx] = PeakOrgArray[OrgIdx]
        else:
            print("Warning: Peak number " + str(OrgIdx+1) +" is predicted in hole size " +str(CurrentHole) +" mm")
            FinalPeaks[OrgIdx] = PreicatedPeaks[OrgIdx]
    
    #Maybe this should be treated the same way as above but al leave it as it is for now
    TrothOrgArray = [None,None,None]
    for trough in Troughs:
        for I in range(3):
            if trough >= FinalPeaks[I] and trough < FinalPeaks[I+1]:
                TrothOrgArray[I] = trough
    
    FinalTroughs=[None,None,None]
    for OrgIdx in range(0,len(FinalTroughs)):
        if TrothOrgArray[OrgIdx]!=None:
            FinalTroughs[OrgIdx] = TrothOrgArray[OrgIdx]
        else:
            print("Warning: Trough number " + str(OrgIdx+1) +" is predicted in hole size " +str(CurrentHole) +" mm")
            FinalTroughs[OrgIdx] = PreicatedTroughs[OrgIdx]


    y_interp = scipy.interpolate.interp1d(np.arange(len(Lines)), Lines)

    #plt.close("all")
    #plt.plot(Lines)
    #plt.plot(Peaks,Lines[Peaks],"x",linestyle="")
    #plt.show()

    PeaksTroughsX = []
    PeaksTroughsY=[]
    MeanPeak = 0
    for peak in FinalPeaks:
        MeanPeak+=y_interp(peak)
        PeaksTroughsX.append(peak)
        PeaksTroughsY.append(y_interp(peak))
    MeanPeak/=4

    MeanTrough=0
    for Troughs in FinalTroughs:
        MeanTrough+=y_interp(Troughs)
        PeaksTroughsX.append(Troughs)
        PeaksTroughsY.append(y_interp(Troughs))

    MeanTrough/=4
    Amplitude = MeanPeak-MeanTrough
    return Amplitude/MeanPeak,MeanPeak,MeanTrough,PeaksTroughsX,PeaksTroughsY


def ExtractLines(Rect,points,values,img):
    Vertical=False
    if Rect.get_width() < Rect.get_height():
        Vertical=True

    StartPoint = list(Rect.get_xy())
    EndPoint = [Rect.get_xy()[0]+Rect.get_width(),Rect.get_xy()[1]+Rect.get_height()]
    IterationAxis = 1 #This is going to determine if we iterate along x or y (horizontal or verticlal lines)
    if Vertical==True:
        IterationAxis=0

    if IterationAxis==1 and StartPoint[IterationAxis] <0:
        StartPoint[IterationAxis]=0
    if IterationAxis==0 and EndPoint[IterationAxis] >=img.shape[1]-1:
        EndPoint[IterationAxis]=img.shape[1]-1

    #The number of samples we do should be equal to the number of pixels, its all the data we have so this makes sense i think?
    NumberOfPixelsInRange = math.floor(EndPoint[IterationAxis]-StartPoint[IterationAxis]) 

    if Vertical==False:
        xvalues=np.linspace(0,xCutoff,math.ceil(xCutoff),endpoint=True)
        IterRange = np.linspace(StartPoint[IterationAxis],EndPoint[IterationAxis],NumberOfPixelsInRange,endpoint=False)
        Lines=np.zeros(xvalues.shape[0])
    else:
        yvalues=np.linspace(yCutoff,img.shape[0]-1,math.ceil(img.shape[0]-yCutoff-1),endpoint=True)
        IterRange = np.linspace(EndPoint[IterationAxis],StartPoint[IterationAxis],NumberOfPixelsInRange,endpoint=False)
        Lines=np.zeros(yvalues.shape[0])
    ##Checking iterRang and x range are right
    for IterValue in IterRange:
        if Vertical==False:
            yvalues=[IterValue]*len(xvalues)
        else:
            xvalues=[IterValue]*len(yvalues)
        Line = griddata(points, values, (yvalues, xvalues), method='linear')
        Lines += Line
    return Lines

ContrastResponsesHorAllRes=[]
ContrastResponsesVertAllRes=[]
ProcessedSizes=[]

LineTest=[]

for I in range(0,4):
    img = imgs[I]

    #plt.close("all")
    #plt.imshow(img)
    #plt.show()

    PixelSteps = HoleSize[I]/res
    StepSize = PixelSteps
    colors = ['r','g','b','y']
    ProcessedSizes.append(HoleSize[I])

    yCutoff = None
    xCutoff = None

    y= -PixelSteps*0.5
    x = img.shape[0]-PixelSteps*1.5

    yCutoff = y + (PixelSteps*2)*3
    xCutoff = (x- PixelSteps*6) + (PixelSteps*2)

    ax0 = fig.add_subplot(gs[0, I])
    ax0.imshow(img)
    ax0.set_title("Hole Size: " + str(HoleSize[I])+" mm")
    
    MiddlesHor = []
    MiddlesVert= []

    y = -PixelSteps*0.5
    x = img.shape[0]-PixelSteps*1.5

    AllLinesAndResultsHor = []
    ContrastResponseResultsHor = []
    AllLinesAndResultsVert = []
    ContrastResponseResultsVert = []

    points=[]
    values=[]
    #Set up Interpolation, im sure there is a far better way of doing this in a more python way...
    for X in range(img.shape[1]):
        for Y in range(img.shape[0]):
            points.append([Y,X])
            values.append(img[Y,X])

    for i in range(4):
        rect = patches.Rectangle((0, y), xCutoff, PixelSteps*2, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="-")
        MiddlesHor.append( (y+(y+PixelSteps*2.0))/2.0)
        ax0.add_patch(rect)
        
        Lines = ExtractLines(rect,points,values,img)
        LineTest.append(Lines)
        y += PixelSteps*2

        AllLinesAndResultsHor.append([Lines,None,None,None,None])
        ContrastResponseResultsHor.append(None)
        ContrastResponseResultsHor[-1], AllLinesAndResultsHor[-1][1], AllLinesAndResultsHor[-1][2], AllLinesAndResultsHor[-1][3], AllLinesAndResultsHor[-1][4] = GetContrastResponseFactor(Lines,PixelSteps,HoleSize[I])
        
        rect = patches.Rectangle((x, yCutoff), PixelSteps*2, img.shape[1]-2-yCutoff, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="--")
        MiddlesVert.append( (x+(x+PixelSteps*2.0))/2.0)
        ax0.add_patch(rect)
        x -= PixelSteps*2

        Lines = ExtractLines(rect,points,values,img)
        AllLinesAndResultsVert.append([Lines,None,None,None,None])
        ContrastResponseResultsVert.append(None)
        ContrastResponseResultsVert[-1], AllLinesAndResultsVert[-1][1], AllLinesAndResultsVert[-1][2], AllLinesAndResultsVert[-1][3], AllLinesAndResultsVert[-1][4] = GetContrastResponseFactor(Lines,PixelSteps,HoleSize[I])

    BestHorIndex=ContrastResponseResultsHor.index(max(ContrastResponseResultsHor))
    BestVertIndex=ContrastResponseResultsVert.index(max(ContrastResponseResultsVert))
    
    ax_hor = fig.add_subplot(gs[1, I])
    ax_hor.plot(AllLinesAndResultsHor[BestHorIndex][0],color="g",linestyle="-")
    ax_hor.axhline(y=AllLinesAndResultsHor[BestHorIndex][1], color='r', linestyle='-')
    ax_hor.axhline(y=AllLinesAndResultsHor[BestHorIndex][2], color='b', linestyle='-')
    ax_hor.plot(AllLinesAndResultsHor[BestHorIndex][3],AllLinesAndResultsHor[BestHorIndex][4],marker="x", color="orange",linestyle="")
    ax_hor.get_yaxis().set_visible(False)
    ax0.plot([0,xCutoff],[MiddlesHor[BestHorIndex],MiddlesHor[BestHorIndex]],linestyle = "-",color="g")

    ax_vert = fig.add_subplot(gs[2, I])
    ax_vert.plot(AllLinesAndResultsVert[BestVertIndex][0],color="g",linestyle="--")
    ax_vert.axhline(y=AllLinesAndResultsVert[BestVertIndex][1], color='r', linestyle='-')
    ax_vert.axhline(y=AllLinesAndResultsVert[BestVertIndex][2], color='b', linestyle='-')
    ax_vert.plot(AllLinesAndResultsVert[BestVertIndex][3],AllLinesAndResultsVert[BestVertIndex][4],marker="x", color="orange",linestyle="")
    ax_vert.get_yaxis().set_visible(False)
    ax0.plot([MiddlesVert[BestVertIndex],MiddlesVert[BestVertIndex]],[yCutoff,len(img)-1],linestyle = "--",color="g")

    ContrastResponsesHorAllRes.append(max(ContrastResponseResultsHor))
    ContrastResponsesVertAllRes.append(max(ContrastResponseResultsVert))

AxOverall = fig.add_subplot(gs[3,:])
AxOverall.plot(ProcessedSizes,ContrastResponsesHorAllRes,marker="x",linestyle="-",label="Horizontal Contrast Response")
AxOverall.plot(ProcessedSizes,ContrastResponsesVertAllRes,marker="x",linestyle="-",label="Vertical Contrast Response")
AxOverall.set_xlim(1.2,0.7)
AxOverall.legend()
AxOverall.set_ylabel("Contrast Response")
AxOverall.set_xlabel("Resolution")
plt.show()