import pydicom
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np

file = "MedACRTestingSetAndResults\Blair Gartnavel\IM_0038"
data = pydicom.dcmread(file).pixel_array
points = []
values = []
for x in range(data.shape[1]):
    for y in range(data.shape[0]):
        points.append((x,y))
        values.append(data[y,x])

def GetContrastResponse(Pointsfiles,OneDir=False):
    Contrast = []
    for Pointsfile in Pointsfiles:
        print(Pointsfile)
        lines = open(Pointsfile).readlines()
        Range = 2
        if OneDir==True:
            Range = 1
        for j in range(Range):
            Peaks = []
            Troughs = []
            for i in range(7+j*7):
                if i == 0+j*7 or i == 2+j*7 or i == 4+j*7 or i ==6+j*7:
                    Peaks.append( (float(lines[i+1].split(",")[1].replace("\n","")) , float(lines[i+1].split(",")[2] )))
                if i == 1+j*7 or i == 3+j*7 or i == 5+j*7 or i ==7+j*7:
                    Troughs.append( (float(lines[i+1].split(",")[1].replace("\n","")) , float(lines[i+1].split(",")[2] )))

            PeakData = griddata(points, values, Peaks, method='linear')
            TroughData = griddata(points, values, Troughs, method='linear')
            Amp = np.mean(PeakData) - np.mean(TroughData)
            Contrast.append( Amp/np.mean(PeakData))

            #plt.imshow(data)
            #plt.plot([Peaks[0][0]],[Peaks[0][1]],marker="x")
            #plt.show()

    return Contrast

files = [ 
"MedACRTestingSetAndResults\SpatialResTolerance\\1.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\2.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\3.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\4.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\5.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\6.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\7.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\8.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\9.csv",
"MedACRTestingSetAndResults\SpatialResTolerance\\10.csv",
]
#Contrast = GetContrastResponse(files,OneDir=True)
#print(Contrast)
#print(np.std(Contrast))

#Contrast = GetContrastResponse(["MedACRTestingSetAndResults\SpatialResTesting\Gartnavel\\1.1mmImageJ.csv"])
#print(Contrast)

Contrast = GetContrastResponse(["MedACRTestingSetAndResults\SpatialResTesting\Gartnavel\\1.0mmImageJ.csv"])
print(Contrast)

Contrast = GetContrastResponse(["MedACRTestingSetAndResults\SpatialResTesting\Gartnavel\\0.9mmImageJ.csv"])
print(Contrast)

Contrast = GetContrastResponse(["MedACRTestingSetAndResults\SpatialResTesting\Gartnavel\\0.8mmImageJ.csv"])
print(Contrast)