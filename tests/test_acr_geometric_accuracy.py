import os
import unittest
import pathlib
import pydicom
import numpy as np

from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_geometric_accuracy import ACRGeometricAccuracy
from hazenlib.ACRObject import ACRObject
from tests import TEST_DATA_DIR, TEST_REPORT_DIR
from hazenlib.tasks.acr_geometric_accuracy_MagNetMethod import ACRGeometricAccuracyMagNetMethod

class TestACRGeometricAccuracySiemens(unittest.TestCase):
    L1 = 192.38, 188.48
    L5 = 192.38, 188.48, 190.43, 192.38
    distortion_metrics = [0.75, 2.38, 0.92]

    def setUp(self):
        ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "Siemens")
        siemens_files = get_dicom_files(ACR_DATA_SIEMENS)

        self.acr_geometric_accuracy_task = ACRGeometricAccuracy(
            input_data=siemens_files,
            report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR),
        )

        self.dcm_1 = self.acr_geometric_accuracy_task.ACR_obj.dcms[0]
        self.dcm_5 = self.acr_geometric_accuracy_task.ACR_obj.dcms[4]

    def test_geometric_accuracy_slice_1(self):
        slice1_vals = self.acr_geometric_accuracy_task.get_geometric_accuracy_slice1(
            self.dcm_1
        )
        slice1_vals = np.round(slice1_vals, 2)

        print("\ntest_geo_accuracy.py::TestGeoAccuracy::test_geo_accuracy_slice1")
        print("new_release:", slice1_vals)
        print("fixed value:", self.L1)

        assert (slice1_vals == self.L1).all() == True

    def test_geometric_accuracy_slice_5(self):
        slice5_vals = np.array(
            self.acr_geometric_accuracy_task.get_geometric_accuracy_slice5(self.dcm_5)
        )
        slice5_vals = np.round(slice5_vals, 2)

        print("\ntest_geo_accuracy.py::TestGeoAccuracy::test_geo_accuracy_slice5")
        print("new_release:", slice5_vals)
        print("fixed value:", self.L5)
        assert (slice5_vals == self.L5).all() == True

    def test_distortion_metrics(self):
        metrics = np.array(
            self.acr_geometric_accuracy_task.distortion_metric(self.L1 + self.L5)
        )

        if self.acr_geometric_accuracy_task.ACR_obj.MediumACRPhantom==True:
                    metrics = np.array(self.acr_geometric_accuracy_task.distortion_metric_MedPhantom(self.L1 + self.L5))

        metrics = np.round(metrics, 2)
        print(metrics)
        assert (metrics == self.distortion_metrics).all() == True


# TODO: Add unit tests for Philips datasets.


class TestACRGeometricAccuracyGE(TestACRGeometricAccuracySiemens):
    L1 = 191.44, 191.44
    L5 = 191.44, 191.44, 191.44, 189.41
    distortion_metrics = [1.1, 1.44, 0.4]

    def setUp(self):
        ACR_DATA_GE = pathlib.Path(TEST_DATA_DIR / "acr" / "GE")
        ge_files = get_dicom_files(ACR_DATA_GE)

        self.acr_geometric_accuracy_task = ACRGeometricAccuracy(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
        )

        self.dcm_1 = self.acr_geometric_accuracy_task.ACR_obj.dcms[0]
        self.dcm_5 = self.acr_geometric_accuracy_task.ACR_obj.dcms[4]


class TestMedACRGeometricAccuracyGE(TestACRGeometricAccuracySiemens):
    L1 = 164.07, 164.07
    L5 = 166.02, 165.05, 166.02, 166.02
    distortion_metrics = [0.21, 1.02, 0.53]

    def setUp(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")
        ge_files = get_dicom_files(ACR_DATA_Med)

        self.acr_geometric_accuracy_task = ACRGeometricAccuracy(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
            ,MediumACRPhantom=True
        )

        self.dcm_1 = self.acr_geometric_accuracy_task.ACR_obj.dcms[0]
        self.dcm_5 = self.acr_geometric_accuracy_task.ACR_obj.dcms[4]


class TestMedACRGeometricAccuracyGEMagNet(unittest.TestCase):

    Results = {'distortion': {'distortion values': {'vertical CoV': 0.15, 'horizontal CoV': 0.28}, 'linearity values': {'Mean Vertical Distance mm': 79.93, 'Mean Horizontal Distance mm': 79.84}, 'horizontal distances mm': [79.58, 79.99, 79.93], 'vertical distances mm': [79.81, 79.94, 80.05]}}
    def setUp(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")
        ge_files = get_dicom_files(ACR_DATA_Med)
        self.acr_geometric_accuracy_task = ACRGeometricAccuracyMagNetMethod(
            input_data=ge_files, report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR)
            ,MediumACRPhantom=True
        )
        self.dcm_1 = self.acr_geometric_accuracy_task.ACR_obj.dcms[0]
        self.dcm_5 = self.acr_geometric_accuracy_task.ACR_obj.dcms[4]

    def test_geometric_accuracy_slice_1(self):
        result = self.acr_geometric_accuracy_task.run()
        assert (result['measurement']['distortion']['distortion values']['vertical CoV'] == self.Results['distortion']['distortion values']['vertical CoV']) == True
        assert (result['measurement']['distortion']['distortion values']['horizontal CoV'] == self.Results['distortion']['distortion values']['horizontal CoV']) == True

        assert (result['measurement']['distortion']['linearity values']['Mean Vertical Distance mm'] == self.Results['distortion']['linearity values']['Mean Vertical Distance mm']) == True
        assert (result['measurement']['distortion']['linearity values']['Mean Horizontal Distance mm'] == self.Results['distortion']['linearity values']['Mean Horizontal Distance mm']) == True
        
        assert (result['measurement']['distortion']['horizontal distances mm'] == self.Results['distortion']['horizontal distances mm']) == True
        assert (result['measurement']['distortion']['vertical distances mm'] == self.Results['distortion']['vertical distances mm']) == True
        