import os
import unittest
import pathlib
import pydicom
import numpy as np
import copy
import glob 

from hazenlib import HazenTask
from hazenlib.ACRObject import ACRObject
from tests import TEST_DATA_DIR, TEST_REPORT_DIR


class TestACRTools(unittest.TestCase):
    rotation = [-1.0, 0.0]
    centre = [(129, 130), (253, 255)] #Had to change these because of a bug fix with the rounding
    test_point = (-60.98, -45.62)

    def setUp(self):
        self.Siemens_data = [
            pydicom.read_file(os.path.join(TEST_DATA_DIR, "acr", "Siemens", f"{i}"))
            for i in os.listdir(os.path.join(TEST_DATA_DIR, "acr", "Siemens"))
        ]
        self.GE_data = [
            pydicom.read_file(os.path.join(TEST_DATA_DIR, "acr", "GE", f"{i}"))
            for i in os.listdir(os.path.join(TEST_DATA_DIR, "acr", "GE"))
        ]

        self.MedACR_data = []
        dcm_files = glob.glob(os.path.join(TEST_DATA_DIR, "MedACR","*.dcm"))
        for file in dcm_files:
            self.MedACR_data.append(pydicom.read_file(file))
        self.MedACR_data_noRot = copy.deepcopy(self.MedACR_data)

        self.Siemens_ACR_obj = ACRObject(self.Siemens_data)
        self.GE_ACR_obj = ACRObject(self.GE_data)

        Keywords = {"MediumACRPhantom": True, "settings":{"RotCorrection":True}}
        self.MedACR_data_obj = ACRObject(self.MedACR_data,Keywords)

        Keywords = {"MediumACRPhantom": True, "settings":{"RotCorrection":False}}
        self.MedACR_NoRot_data_obj = ACRObject(self.MedACR_data_noRot,Keywords)

    def test_find_rotation(self):
        assert self.rotation[0] == np.round(
            self.Siemens_ACR_obj.determine_rotation(), 1
        )
        assert self.rotation[1] == np.round(self.GE_ACR_obj.determine_rotation(), 1)

    def test_find_centre(self):
        assert (
            self.centre[0] == np.round(self.Siemens_ACR_obj.centre, 1)
        ).all() == True
        assert (self.centre[1] == np.round(self.GE_ACR_obj.centre, 1)).all() == True

    def test_rotate_point(self):
        rotated_point = np.array(
            self.Siemens_ACR_obj.rotate_point((0, 0), (30, 70), 150)
        )
        rotated_point = np.round(rotated_point, 2)
        assert (rotated_point == self.test_point).all() == True

    def test_rotate_images(self):
        assert self.MedACR_data_obj.determine_rotation() == 0.0