import os
import sys
import traceback
import pydicom

import numpy as np
from scipy import ndimage
import SimpleITK as sitk
import hazenlib.utils
from hazenlib.HazenTask import HazenTask
from hazenlib.ACRObject import ACRObject
from pydicom.pixel_data_handlers.util import apply_modality_lut

class ACRCNR(HazenTask):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ACR_obj = ACRObject(self.dcm_list,kwargs)

    def run(self) -> dict:
        ContrastSliceDCM = self.ACR_obj.dcm_list[-1]
        RefDicom = pydicom.dcmread("_internal\\StandardDicom\\IM_0048")

        fixed = sitk.GetImageFromArray(ContrastSliceDCM.pixel_array.astype(np.float32))
        moving = sitk.GetImageFromArray(RefDicom.pixel_array.astype(np.float32))