import os
import unittest
import pathlib
import pydicom
import numpy as np

from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
from hazenlib.ACRObject import ACRObject
from tests import TEST_DATA_DIR, TEST_REPORT_DIR
from hazenlib.tasks.acr_spatial_resolution import ResOptions


class TestACRSpatialResolutionSiemens(unittest.TestCase):
    centre = (128, 124)
    rotation_angle = 9
    y_ramp_pos = 118
    width = 13
    edge_type = "vertical", "downward"
    edge_loc = [5, 7]
    slope = -0.165
    MTF50 = (1.18, 1.35)

    def setUp(self):
        ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "SiemensMTF")
        siemens_files = get_dicom_files(ACR_DATA_SIEMENS)

        self.acr_spatial_resolution_task = ACRSpatialResolution(
            input_data=siemens_files,
            report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR),
        )

        self.dcm = self.acr_spatial_resolution_task.ACR_obj.dcms[0]
        self.crop_image = self.acr_spatial_resolution_task.crop_image(
            self.dcm.pixel_array, self.centre[0], self.y_ramp_pos, self.width
        )
        self.data = self.dcm.pixel_array
        self.res = self.dcm.PixelSpacing

    def test_find_y_ramp(self):
        y_ramp_pos = self.acr_spatial_resolution_task.y_position_for_ramp(
            self.res, self.data, self.centre
        )
        assert y_ramp_pos == self.y_ramp_pos

    def test_get_edge_type(self):
        edge_type = self.acr_spatial_resolution_task.get_edge_type(self.crop_image)
        assert edge_type == self.edge_type

    def test_get_edge_loc(self):
        assert (
            self.acr_spatial_resolution_task.edge_location_for_plot(
                self.crop_image, self.edge_type[0] == self.edge_loc
            )
        ).all()

    def test_retrieve_slope(self):
        slope = self.acr_spatial_resolution_task.fit_normcdf_surface(
            self.crop_image, self.edge_type[0], self.edge_type[1]
        )[0]
        assert np.round(slope, 3) == self.slope

    def test_get_MTF50(self):
        mtf50 = self.acr_spatial_resolution_task.get_mtf50(self.dcm)
        rounded_mtf50 = (np.round(mtf50[0], 2), np.round(mtf50[1], 2))

        print("\ntest_get_MTF50.py::TestGetMTF50::test_get_MTF50")
        print("new_release_value:", rounded_mtf50)
        print("fixed_value:", self.MTF50)

        assert rounded_mtf50 == self.MTF50


class TestACRSpatialResolutionGE(TestACRSpatialResolutionSiemens):
    centre = (254, 255)
    rotation_angle = 0
    y_ramp_pos = 244
    width = 26
    edge_type = "vertical", "upward"
    edge_loc = [5, 7]
    slope = 0.037
    MTF50 = (0.72, 0.71)

    def setUp(self):
        ACR_DATA_GE = pathlib.Path(TEST_DATA_DIR / "acr" / "GE")
        ge_files = get_dicom_files(ACR_DATA_GE)

        self.acr_spatial_resolution_task = ACRSpatialResolution(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
        )

        self.dcm = self.acr_spatial_resolution_task.ACR_obj.dcms[0]
        self.crop_image = self.acr_spatial_resolution_task.crop_image(
            self.dcm.pixel_array, self.centre[0], self.y_ramp_pos, self.width
        )
        self.data = self.dcm.pixel_array
        self.res = self.dcm.PixelSpacing


class TestMedACRSpatialResolution(unittest.TestCase):
    DotMatrixResult = {'task': 'ACRSpatialResolution', 'file': 'ACR_AxT1_4_1', 'measurement': {'1.1mm holes': 2524630.81, '1.0mm holes': 1230470.89, '0.9mm holes': 284317.18, '0.8mm holes': 391006.3}}
    ContrastResponseResult = {'task': 'ACRSpatialResolution', 'file': 'ACR_AxT1_4_1', 'measurement': {'1.1mm holes Horizontal': 65.21, '1.1mm holes Vertical': 33.85, '1.0mm holes Horizontal': 65.07, '1.0mm holes Vertical': 14.78, '0.9mm holes Horizontal': 18.25, '0.9mm holes Vertical': 7.39, '0.8mm holes Horizontal': 2.75, '0.8mm holes Vertical': 3.61}}
    def setUp(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")
        ge_files = get_dicom_files(ACR_DATA_Med)

        self.acr_spatial_resolution_task = ACRSpatialResolution(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR),report=False
            ,MediumACRPhantom=True
        )
        
    
    def test_DotMatrix(self):
        self.acr_spatial_resolution_task.ResOption=ResOptions.DotMatrixMethod
        Res =  self.acr_spatial_resolution_task.run()
        assert Res == self.DotMatrixResult

    def test_ContrastResponse(self):
        self.acr_spatial_resolution_task.ResOption=ResOptions.ContrastResponseMethod
        Res =  self.acr_spatial_resolution_task.run()
        print(Res)
        assert Res == self.ContrastResponseResult