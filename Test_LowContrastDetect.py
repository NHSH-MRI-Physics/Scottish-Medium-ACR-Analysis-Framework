import os
import sys
import traceback
from unittest import result
import pydicom
import matplotlib.pyplot as plt
import SimpleITK as sitk
import numpy as np
#RefDicom = pydicom.dcmread("_internal\\StandardDicom\\IM_0048")
#plt.imshow(RefDicom.pixel_array)
#plt.show()
from scipy import ndimage
#import hazenlib.utils
#from hazenlib.HazenTask import HazenTask
#from hazenlib.ACRObject import ACRObject
from pydicom.pixel_data_handlers.util import apply_modality_lut
from scipy import ndimage
from skimage import filters
import math


ref3d = sitk.ReadImage("_internal\\StandardDicom\\I1100000")
input3d = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0048")

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

RefPhysPoints =[ [130.86,116.22],
                    [136.72,121.10],
                    [137.70,128.91],
                    [134.77,135.75],
                    [127.93,139.65],
                    [120.12,138.68],
                    [114.26,133.79],
                    [112.31,125.98],
                    [116.22,118.17],
                    [123.05,115.24]
                ]#In phys space in mm
RefPhysIdx = []
for RefPhys in RefPhysPoints:
    RefIdx = refimage.TransformPhysicalPointToIndex(RefPhys)
    RefPhysIdx.append(RefIdx)
RefIdx = refimage.TransformPhysicalPointToIndex(RefPhys)

fixed_array = sitk.GetArrayFromImage(refimage)
moving_array = sitk.GetArrayFromImage(inputimage)
result_array = sitk.GetArrayFromImage(result)

'''
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
axs[0].imshow(fixed_array, cmap="gray"); axs[0].set_title("Fixed (this is the reference image)"); axs[0].axis("off")
for RefIdx in RefPhysIdx:
    axs[0].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.5)  # Plot the test point on the moving image
axs[1].imshow(moving_array, cmap="gray"); axs[1].set_title("Moving (this is our input image)"); axs[1].axis("off")
axs[2].imshow(fixed_array, cmap="gray")
axs[2].imshow(result_array, cmap="Blues", alpha=0.3)
for RefIdx in RefPhysIdx:
    axs[2].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.5)  # Plot the test point on the moving image
plt.show()
'''

from dataclasses import dataclass
@dataclass
class Disc:
    Diamater: float
    crop: float
    x:float
    y:float
    SpokeNumber: int
    SpokeDepth: str

Radii =[7.0]

Pixels = math.ceil((7.0/moving.GetSpacing()[0]/2.0)*1.5)
Spoke1 = Disc(Diamater=7.0, crop=result_array[RefPhysIdx[0][1]-Pixels:RefPhysIdx[0][1]+Pixels,RefPhysIdx[0][0]-Pixels:RefPhysIdx[0][0]+Pixels], x=0.0, y=0.0, SpokeNumber=1, SpokeDepth="inner")