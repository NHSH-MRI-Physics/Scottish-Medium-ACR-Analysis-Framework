import os
import sys
import traceback
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

class ACRCNR(HazenTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ACR_obj = ACRObject(self.dcm_list,kwargs)

    def run(self) -> dict:
        ContrastSliceDCM = self.ACR_obj.dcms[-1]
        RefDicom = pydicom.dcmread("_internal\\StandardDicom\\IM_0048")