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
import hazenlib.utils
from hazenlib.HazenTask import HazenTask
from hazenlib.ACRObject import ACRObject
from pydicom.pixel_data_handlers.util import apply_modality_lut
from scipy import ndimage
from skimage import filters

class ACRCNR(HazenTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ACR_obj = ACRObject(self.dcm_list,kwargs)

    def run(self) -> dict:
        '''
        inputSlice = self.ACR_obj.dcms[-1]
        crop = inputSlice.pixel_array[self.ACR_obj.centre[1]-50:self.ACR_obj.centre[1]+50,self.ACR_obj.centre[0]-50:self.ACR_obj.centre[0]+50]
        Thresh = filters.threshold_otsu(crop)
        mask = crop > Thresh
        labels, nb = ndimage.label(mask)

        find_objects = ndimage.find_objects(labels)
        from dataclasses import dataclass
        @dataclass
        class TestObject:
            x: float
            y: float
            Diamater: float
            disanceFromCentre: float
        
        Objects = []
        for object in find_objects:
            center = [(obj.start + obj.stop - 1) / 2 for obj in object]
            Diameter = ((object[0].stop - object[0].start) + (object[1].stop - object[1].start))/2.0
            Dist =  (25 - center[1])**2 + (25 - center[0])**2
            TestObj = TestObject(x=center[1],y=center[0],Diamater=Diameter,disanceFromCentre=Dist)
            Objects.append(TestObj)
        Objects.sort(key=lambda x: x.disanceFromCentre, reverse=False)
        #Objects = Objects[:10]

        plt.imshow(crop, cmap="gray")
        for Obj in Objects:
            plt.plot(Obj.x,Obj.y, 'rx')
            circle = plt.Circle((Obj.x,Obj.y), Obj.Diamater/2.0, fill=False)
            plt.gca().add_patch(circle)
        
        
        plt.savefig("test.png",dpi=300)

        '''
        #This was the attempt using the registration, its prob massivley overengineerd so al leave it here incase i want to revert..
        input3d = sitk.GetImageFromArray(self.ACR_obj.dcms[-1].pixel_array)
        refDcm = pydicom.dcmread("_internal\\StandardDicom\\I1100000")
        ref3d = sitk.GetImageFromArray(refDcm.pixel_array)

        extract = sitk.ExtractImageFilter()
        extract.SetSize([ref3d.GetSize()[0], ref3d.GetSize()[1], 0])
        extract.SetIndex([0, 0, 0])
        fixed = extract.Execute(ref3d)

        extract = sitk.ExtractImageFilter()
        extract.SetSize([input3d.GetSize()[0], input3d.GetSize()[1], 0])
        extract.SetIndex([0, 0, 0])
        moving = extract.Execute(input3d)

        moving.SetOrigin((0.0, 0.0))
        fixed.SetOrigin((0.0, 0.0))

        #spacing
        moving.SetSpacing(self.ACR_obj.dcms[-1].PixelSpacing)
        fixed.SetSpacing(refDcm.PixelSpacing)

        # direction
        iop = list(map(float, self.ACR_obj.dcms[-1].ImageOrientationPatient))
        row = np.array(iop[:3])
        col = np.array(iop[3:])
        direction = [row[0], col[0],row[1], col[1]]
        moving.SetDirection(direction)

        iop = list(map(float, refDcm.ImageOrientationPatient))
        row = np.array(iop[:3])
        col = np.array(iop[3:])
        direction = [row[0], col[0],row[1], col[1]]
        fixed.SetDirection(direction)

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

        fixed_array = sitk.GetArrayFromImage(refimage)
        moving_array = sitk.GetArrayFromImage(inputimage)
        result_array = sitk.GetArrayFromImage(result)
        '''
        '''
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        axs[0].imshow(fixed_array, cmap="gray"); axs[0].set_title("Fixed (this is the reference image)"); axs[0].axis("off")
        for RefIdx in RefPhysIdx:
            axs[0].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.2)  # Plot the test point on the moving image
        axs[1].imshow(moving_array, cmap="gray"); axs[1].set_title("Moving (this is our input image)"); axs[1].axis("off")
        axs[2].imshow(fixed_array, cmap="gray")
        axs[2].imshow(result_array, cmap="Blues", alpha=0.3)
        for RefIdx in RefPhysIdx:
            axs[2].plot(RefIdx[0], RefIdx[1], 'rx',ms=0.2)  # Plot the test point on the moving image
        plt.savefig("test.png",dpi=300)
        
        