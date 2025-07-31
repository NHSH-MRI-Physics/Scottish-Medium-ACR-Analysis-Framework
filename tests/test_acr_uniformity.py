import os
import unittest
import pathlib
import pydicom

from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.ACRObject import ACRObject
from tests import TEST_DATA_DIR, TEST_REPORT_DIR
from MedACROptions import UniformityOptions

class TestACRUniformitySiemens(unittest.TestCase):
    piu = 67.43 #Had to change this beacause of a bug fix in ACRObjects circular_mask

    def setUp(self):
        ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "Siemens")
        siemens_files = get_dicom_files(ACR_DATA_SIEMENS)

        self.acr_uniformity_task = ACRUniformity(
            input_data=siemens_files,
            report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR),
        )

    def test_uniformity(self):
        results, _, _, _, _ = self.acr_uniformity_task.get_integral_uniformity(
            self.acr_uniformity_task.ACR_obj.slice7_dcm
        )
        rounded_results = round(results, 2)

        print("\ntest_uniformity.py::TestUniformity::test_uniformity")
        print("new_release_values:", rounded_results)
        print("fixed_values:", self.piu)

        assert rounded_results == self.piu


# TODO: Add unit tests for Philips datasets.
class TestACRUniformityGE(TestACRUniformitySiemens):
    piu = 84.66 #Had to change this beacause of a bug fix in ACRObjects circular_mask

    def setUp(self):
        ACR_DATA_GE = pathlib.Path(TEST_DATA_DIR / "acr" / "GE")
        ge_files = get_dicom_files(ACR_DATA_GE)
    
        self.acr_uniformity_task = ACRUniformity(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
        )

class TestMedACRUniformity(TestACRUniformitySiemens):
    #piu = 75.9
    piu = 76.33
    def setUp(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")
        ge_files = get_dicom_files(ACR_DATA_Med)
    
        self.acr_uniformity_task = ACRUniformity(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
            ,MediumACRPhantom=True
        )

class TestMedACRMagfNetUniformity(unittest.TestCase):
    def test_uniformity(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")
        ge_files = get_dicom_files(ACR_DATA_Med)
        acr_uniformity_task = ACRUniformity(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
            ,MediumACRPhantom=True
        )
        acr_uniformity_task.UniformityMethod = UniformityOptions.MAGNETMETHOD
        Results = acr_uniformity_task.run()

        assert Results['measurement']['Horizontal Uniformity %'] == 84.03
        assert Results['measurement']['Vertical Uniformity %'] == 22.79
