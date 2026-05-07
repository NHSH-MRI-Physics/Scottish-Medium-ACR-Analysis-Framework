import SimpleITK as sitk
from matplotlib import patches
import matplotlib.pyplot as plt
from dataclasses import dataclass
import math
import numpy as np
import matplotlib.colors as mcolors

@dataclass
class Disc:
    Diamater: float
    crop: float
    x:float
    y:float
    SpokeNumber: int
    SpokeDepth: str
    CropSize: int

#This is the centre of each disk in slice 11 in mm
RefPhysPointsSlice11 =[ [[130.86,116.22],[137.01,104.97],[142.27,93.17]],
                        [[136.72,121.10],[148.55,115.60],[159.64,109.44]],
                        [[137.70,128.91],[151.21,131.82],[163.83,133.03]],
                        [[134.77,135.75],[144.23,145.36],[153.51,154.19]],
                        [[127.93,139.65],[130.30,152.66],[132.52,165.35]],
                        [[120.12,138.68],[114.50,150.55],[109.06,161.93]],
                        [[114.26,133.79],[103.32,139.88],[92.25,145.92]],
                        [[112.31,125.98],[100.60,124.07],[88.22,122.46]],
                        [[116.22,118.17],[107.45,110.68],[98.59,101.42]],
                        [[123.05,115.24],[121.53,102.86],[119.21,90.25]]
                    ]
x=[]
y=[]
for Spoke in RefPhysPointsSlice11:
    for RefPhys in Spoke:
        x.append(RefPhys[0])
        y.append(RefPhys[1])
Origin = [np.mean(x),np.mean(y)]

def LoadAndRegisterDCM(ref3d,input3d,adjustpointsangle = 0):
    extract = sitk.ExtractImageFilter()
    extract.SetSize([ref3d.GetSize()[0], ref3d.GetSize()[1], 0])
    extract.SetIndex([0, 0, 0])
    fixed = extract.Execute(ref3d)

    extract = sitk.ExtractImageFilter()
    extract.SetSize([input3d.GetSize()[0], input3d.GetSize()[1], 0])
    extract.SetIndex([0, 0, 0])
    moving = extract.Execute(input3d)

    #Reset the origins to (0,0) to avoid any issues with the registration
    moving.SetOrigin((0.0, 0.0))
    fixed.SetOrigin((0.0, 0.0))

    print("fixed origin:", fixed.GetOrigin())
    print("fixed spacing:", fixed.GetSpacing())
    print("fixed direction:", fixed.GetDirection())

    print("moving origin:", moving.GetOrigin())
    print("moving spacing:", moving.GetSpacing())
    print("moving direction:", moving.GetDirection())

    refimage = sitk.Cast(fixed, sitk.sitkFloat32)
    inputimage = sitk.Cast(moving, sitk.sitkFloat32)

    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(refimage)
    elastixImageFilter.SetMovingImage(inputimage)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("affine"))
    elastixImageFilter.Execute()
    result = elastixImageFilter.GetResultImage()
    

    RefPhysIdx = []
    for Spoke in RefPhysPointsSlice11:
        Temp = []
        for RefPhys in Spoke:
            if adjustpointsangle != 0:
                    qx = Origin[0] + math.cos(math.radians(adjustpointsangle)) * (RefPhys[0] - Origin[0]) - math.sin(math.radians(adjustpointsangle)) * (RefPhys[1] - Origin[1])
                    qy = Origin[1] + math.sin(math.radians(adjustpointsangle)) * (RefPhys[0] - Origin[0]) + math.cos(math.radians(adjustpointsangle)) * (RefPhys[1] - Origin[1])
                    RefPhys = [qx,qy]
            RefIdx = refimage.TransformPhysicalPointToIndex(RefPhys)
            Temp.append(RefIdx)
        RefPhysIdx.append(Temp)
    RefIdx = refimage.TransformPhysicalPointToIndex(RefPhys)
    Origin_Index = refimage.TransformPhysicalPointToIndex(Origin)

    #refimage = sitk.RescaleIntensity(refimage, 0.0, 1.0)
    #inputimage = sitk.RescaleIntensity(inputimage, 0.0, 1.0)
    #result = sitk.RescaleIntensity(result, 0.0, 1.0)

    fixed_array = sitk.GetArrayFromImage(refimage)
    moving_array = sitk.GetArrayFromImage(inputimage)
    result_array = sitk.GetArrayFromImage(result)

    return fixed_array, moving_array, result, RefPhysIdx

def GetDiscCrops(DiscPoints, RegisteredInputImage):
    Radii =[7.0, 6.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5]
    ImageArray = sitk.GetArrayFromImage(RegisteredInputImage)
    SpokeCount = 1
    discs = []
    for SpokeRadius in Radii:
        Centres = DiscPoints[SpokeCount-1]
        CentreCount = 1
        DiscTemp = []
        for centre in Centres:
            CropSize = math.ceil((SpokeRadius/RegisteredInputImage.GetSpacing()[0]/2.0)*1.5)
            CropSize = 6
            Crop = ImageArray[centre[1]-CropSize:centre[1]+CropSize,centre[0]-CropSize:centre[0]+CropSize]

            if CentreCount==1:
                Depth = "inner"
            elif CentreCount==2:
                Depth = "mid"
            else:
                Depth = "outer"

            DiscObj = Disc(Diamater=SpokeRadius, crop=Crop, x=centre[0], y=centre[1], SpokeNumber=SpokeCount, SpokeDepth=Depth,CropSize=6)
            DiscTemp.append(DiscObj)
            CentreCount+=1
        discs.append(DiscTemp)
        SpokeCount+=1

    return discs

def PlotDiscs(Discs,WL,WW,title=""):
    fig, axes = plt.subplots(10, 3, figsize=(6, 20))
    fig.suptitle(title, fontsize=16,y=0.997)
    SpokeCount = 0
    for Spoke in Discs:
        DiscCount = 0
        for disc in Spoke:
            axes[SpokeCount, DiscCount].imshow(disc.crop, cmap="gray",vmax=WL+WW/2.0,vmin=WL-WW/2.0, interpolation='none')
            axes[SpokeCount, DiscCount].axis("off")
            axes[SpokeCount, DiscCount].set_title(f"Spoke {disc.SpokeNumber} - {disc.SpokeDepth}", fontsize=8,y=0.97)
            DiscCount+=1
        SpokeCount+=1
    plt.tight_layout()
    plt.savefig("MedACRTesting\LowContrastDetectTesting\Discs_" + title +".png",dpi=300)
    plt.close()

def PlotRegistration(RefImage_array,InputImage_array,RegisteredInputImage,DiscPoints,title=""):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    axs[0].imshow(RefImage_array, cmap="gray"); axs[0].set_title("Fixed (this is the reference image)"); axs[0].axis("off")
    for Spoke in DiscPoints:
        for RefIdx in Spoke:
            axs[0].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.5)  # Plot the test point on the moving image
    axs[1].imshow(InputImage_array, cmap="gray"); axs[1].set_title("Moving (this is our input image)"); axs[1].axis("off")
    axs[2].imshow(RefImage_array, cmap="gray")
    axs[2].imshow(sitk.GetArrayFromImage(RegisteredInputImage), cmap="Blues", alpha=0.3)
    for Spoke in DiscPoints:
        for RefIdx in Spoke:
            axs[2].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.5)  # Plot the test point on the moving image
    plt.savefig("MedACRTesting\LowContrastDetectTesting\Registration_" + title +".png",dpi=300)
    plt.close()


def PlotSquares(RegisteredInputImage,Discs,WL,WW,title):
    Image = sitk.GetArrayFromImage(RegisteredInputImage)
    if WL == None or WW == None:
        plt.imshow(Image, cmap="gray")
    else:
        plt.imshow(Image, cmap="gray",vmax=WL+WW/2.0,vmin=WL-WW/2.0, interpolation='none')

    colors = [mcolors.to_hex(c) for c in plt.cm.tab10.colors]
    count = 0
    for Spoke in Discs:
        for Disc in Spoke:
            plt.plot(Disc.x, Disc.y, 'rx',ms=1.5, color = colors[count])  # Plot the test point on the moving image
            rect = patches.Rectangle((Disc.x-Disc.CropSize, Disc.y-Disc.CropSize), Disc.CropSize*2.0, Disc.CropSize*2.0, linewidth=1, edgecolor=colors[count], facecolor='none')
            plt.gca().add_patch(rect)
        count +=1
    plt.savefig("MedACRTesting\LowContrastDetectTesting\Squares_" + title +".png",dpi=300)
    plt.close()