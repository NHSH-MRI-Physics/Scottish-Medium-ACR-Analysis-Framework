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

inputdata = "MedACRTesting/TestData/ACR_ARDL_Tests"
Seq = "ACR AxT1 High Res"
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

imgs = [Crops["1.1mm holes"],Crops["1.0mm holes"],Crops["0.9mm holes"],Crops["0.8mm holes"]]
HoleSize = [1.1,1.0,0.9,0.8]

for I in range(1):
    img = imgs[I]
    PixelSteps = HoleSize[I]/0.4883
    StepSize = PixelSteps
    colors = ['r','g','b','y']

    yCutoff = None
    xCutoff = None

    y= -PixelSteps*0.5
    x = img.shape[0]-PixelSteps*1.5

    yCutoff = y + (PixelSteps*2)*3
    xCutoff = (x- PixelSteps*6) + (PixelSteps*2)

    for i in range(4):
        rect = patches.Rectangle((x, yCutoff), PixelSteps*2, img.shape[1]-2-yCutoff, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="--")
        plt.gca().add_patch(rect)
        #xCutoff = x+PixelSteps*2
        x -= PixelSteps*2

    plt.imshow(img)
    plt.ylim(img.shape[1]+2,-4)
    plt.xlim(-2,img.shape[0]+4)
    plt.show()

    #sys.exit()

    #Reset x,y values
    #y= -PixelSteps*0.5
    #x = img.shape[0]-PixelSteps*1.5

    for i in range(4):

        #Horizontal Lines
        ContrastResponseResultsHor = []
        if y < 0:
            Box = img[0:int(round(y+PixelSteps*2))+1,0:int(round(xCutoff))]
        else:
            Box = img[int(round(y)):int(round(y+PixelSteps*2))+1,0:int(round(xCutoff))]


        Lines = np.array(Box[0,:])
        for Y in range(1,Box.shape[0]):
            Lines+=np.array(Box[Y,:])
        
        #All this below should be in a fuunction
        Peaks, PeakProperties = scipy.signal.find_peaks(Lines,distance=PixelSteps)
        Troughs, TroughsProperties = scipy.signal.find_peaks(-Lines,distance=PixelSteps)

        #Peaks=list(np.delete(Peaks,[1]))
        #Troughs=list(np.delete(Troughs,[1]))

        PeaksandTroughs = list(Peaks)+list(Troughs)        
        from scipy.optimize import curve_fit
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
        PeakOrgArray = [ None,None,None,None]
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
                FinalTroughs[OrgIdx] = PreicatedTroughs[OrgIdx]

        import scipy.interpolate
        y_interp = scipy.interpolate.interp1d(np.arange(len(Lines)), Lines)

        MeanPeak = 0
        for peak in FinalPeaks:
            MeanPeak+=y_interp(peak)
        MeanPeak/=4

        MeanTrough=0
        for Troughs in FinalTroughs:
            MeanTrough+=y_interp(Troughs)
        MeanTrough/=4
        Amplitude = MeanPeak-MeanTrough

        ContrastResponseResultsHor.append(Amplitude/MeanPeak)

        plt.plot(Lines)
        plt.plot(x,data_fit)
        plt.axhline(y=MeanPeak, color='r', linestyle='-')
        plt.axhline(y=MeanTrough, color='b', linestyle='-')
        plt.show() 

        rect = patches.Rectangle((0, y), xCutoff, PixelSteps*2, linewidth=1, edgecolor=colors[i], facecolor='none')
        #plt.gca().add_patch(rect)
        y += PixelSteps*2
    
    print(max(ContrastResponseResultsHor))