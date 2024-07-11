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
    yCutoff = y + (PixelSteps*2)*3

    x = img.shape[0]-PixelSteps*1.5
    for i in range(4):
        rect = patches.Rectangle((x, yCutoff), PixelSteps*2, img.shape[1]-2-yCutoff, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="--")
        #plt.gca().add_patch(rect)
        xCutoff = x+PixelSteps*2
        x -= PixelSteps*2

    for i in range(1):
        if y < 0:
            Box = img[0:int(round(y+PixelSteps*2))+1,0:int(round(xCutoff))]
        else:
            Box = img[int(round(y)):int(round(y+PixelSteps*2))+1,0:int(round(xCutoff))]
        
        Lines = np.array(Box[0,:])
        for Y in range(1,Box.shape[0]):
            Lines+=np.array(Box[Y,:])

        Peaks, PeakProperties = scipy.signal.find_peaks(Lines,distance=PixelSteps)
        Troughs, TroughsProperties = scipy.signal.find_peaks(-Lines,distance=PixelSteps)


    
        Peaks = sorted(Peaks)
        Troughs = sorted(Troughs)

        Peaks=list(np.delete(Peaks,[0,1,2]))

        DataToFit = Peaks+Troughs

        #iF > 4 peaks take the 4 highest?
        #if < 4 peaks fit a sin and fill in the gaps
        #Have a special case where 0 peaks are computed (just whack a sin wave down with some guess of phase)
        
        
        if len(Peaks)<4:
            from scipy.optimize import curve_fit
            def Sin(x, phase):
                return np.sin(2*np.pi*x * 1/(PixelSteps*2) + phase) * np.max(Lines)/2 + np.mean(Lines)
            p0=[0]
            fit = curve_fit(Sin, DataToFit, Lines[DataToFit], p0=p0)
            data_fit = Sin(np.arange(0,xCutoff),*fit[0])
        

        plt.plot(Lines)
        plt.plot(data_fit)
        plt.plot(DataToFit,Lines[DataToFit],"x")
        plt.show() 

        rect = patches.Rectangle((0, y), xCutoff, PixelSteps*2, linewidth=1, edgecolor=colors[i], facecolor='none')
        #plt.gca().add_patch(rect)
        y += PixelSteps*2
        
    #plt.imshow(img)
    #plt.ylim(img.shape[1]+2,-4)
    #plt.xlim(-2,img.shape[0]+4)
    #plt.show()