import os
import sys
import traceback
from unittest import result
import pydicom
import matplotlib.pyplot as plt
import SimpleITK as sitk
import numpy as np
from scipy import ndimage
from pydicom.pixel_data_handlers.util import apply_modality_lut
from scipy import ndimage
from skimage import filters
import math
import LowContrastHelpers
import MakeData

ref3d_Slice11 = sitk.ReadImage("_internal\\StandardDicom\\Slice11_ref")
input3d_Slice11 = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0048")

ref3d_Slice10 = sitk.ReadImage("_internal\\StandardDicom\\Slice10_ref")
input3d_Slice10 = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0047")

ref3d_Slice09 = sitk.ReadImage("_internal\\StandardDicom\\Slice09_ref")
input3d_Slice09 = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0046")

ref3d_Slice08 = sitk.ReadImage("_internal\\StandardDicom\\Slice08_ref")
input3d_Slice08 = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0045")


def Process(ref3d,input3d,title,angle=0,WL=None,WW=None):
    RefImage_array,InputImage_array,RegisteredInputImage,DiscPoints = LowContrastHelpers.LoadAndRegisterDCM(ref3d,input3d,angle)
    Discs = LowContrastHelpers.GetDiscCrops(DiscPoints, RegisteredInputImage)
    LowContrastHelpers.PlotRegistration(RefImage_array,InputImage_array,RegisteredInputImage,DiscPoints,title)
    LowContrastHelpers.PlotDiscs(Discs,WL,WW,title)
    LowContrastHelpers.PlotSquares(RegisteredInputImage,Discs,WL,WW,title)


#Process(ref3d_Slice11,input3d_Slice11,"Slice 11", WL = 1551, WW = 228)
#Process(ref3d_Slice10,input3d_Slice10,"Slice 10",angle=-9, WL = 1692, WW = 450)
#Process(ref3d_Slice09,input3d_Slice09,"Slice 09",angle=-18, WL = 1765, WW = 510)
#Process(ref3d_Slice08,input3d_Slice08,"Slice 08",angle=-27,  WL = 1708, WW = 190)

MakeData.TestCircle(1,6)