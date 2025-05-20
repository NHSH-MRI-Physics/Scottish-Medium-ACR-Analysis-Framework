import unittest
import os
import numpy as np
import pydicom
import pathlib
import hazenlib.utils as hazen_tools
from tests import TEST_DATA_DIR
import MedACRAnalysisV2 as MedACRAnalysis
import MedACROptions
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
from tests import TEST_DATA_DIR, TEST_REPORT_DIR
import sys
from PyInstallerGUI import VariableHolder

class ShapeSetUp(unittest.TestCase):
    SMALL_CIRCLE_PHANTOM_FILE = str(
        TEST_DATA_DIR
        / "ghosting"
        / "PE_COL_PHANTOM_BOTTOM_RIGHT"
        / "PE_COL_PHANTOM_BOTTOM_RIGHT.IMA"
    )
    small_circle_x, small_circle_y, small_circle_r = 1, 1, 22.579364776611328

    LARGE_CIRCLE_PHANTOM_FILE = str(TEST_DATA_DIR / "uniformity" / "axial_oil.IMA")
    large_circle_x, large_circle_y, large_circle_r = 128, 123, 97.84805297851562

    SAG_RECTANGLE_PHANTOM_FILE = str(TEST_DATA_DIR / "uniformity" / "sag.dcm")
    rectangle_size = (177.0, 204.0)
    rectangle_angle = 0
    rectangle_centre = (130.500015, 134.499985)

    COR_RECTANGLE_PHANTOM_FILE = str(TEST_DATA_DIR / "uniformity" / "cor.dcm")
    cor_rectangle_size = (206.047546, 194.684875)
    cor_rectangle_angle = -89.1756591796875
    cor_rectangle_centre = (128.43869, 136.219971)

    COR2_RECTANGLE_PHANTOM_FILE = str(TEST_DATA_DIR / "uniformity" / "cor2.dcm")
    cor2_rectangle_size = (194.4591522216797, 201.483292)
    cor2_rectangle_angle = -1.576546
    cor2_rectangle_centre = (127.261551, 130.001953)


# @pytest.mark.skip
class TestShapeDetector(ShapeSetUp):
    def setUp(self) -> None:
        pass

    def test_large_circle(self):
        arr = pydicom.read_file(self.LARGE_CIRCLE_PHANTOM_FILE).pixel_array
        shape_detector = hazen_tools.ShapeDetector(arr=arr)
        x, y, r = shape_detector.get_shape("circle")
        assert int(x), int(y) == (self.large_circle_x, self.large_circle_y)
        assert round(r) == round(self.large_circle_r)

    def test_small_circle(self):
        arr = pydicom.read_file(self.SMALL_CIRCLE_PHANTOM_FILE).pixel_array
        shape_detector = hazen_tools.ShapeDetector(arr=arr)
        x, y, r = shape_detector.get_shape("circle")
        assert int(x), int(y) == (self.small_circle_x, self.small_circle_y)
        assert round(r) == round(self.small_circle_r)

    def test_sag_rectangle(self):
        arr = pydicom.read_file(self.SAG_RECTANGLE_PHANTOM_FILE).pixel_array
        shape_detector = hazen_tools.ShapeDetector(arr=arr)
        centre, size, angle = shape_detector.get_shape("rectangle")
        np.testing.assert_allclose(centre, self.rectangle_centre, rtol=1e-02)
        np.testing.assert_allclose(size, self.rectangle_size, rtol=1e-02)
        np.testing.assert_allclose(angle, self.rectangle_angle, rtol=1e-02)

    def test_cor_rectangle(self):
        arr = pydicom.read_file(self.COR_RECTANGLE_PHANTOM_FILE).pixel_array
        shape_detector = hazen_tools.ShapeDetector(arr=arr)
        centre, size, angle = shape_detector.get_shape("rectangle")
        np.testing.assert_allclose(centre, self.cor_rectangle_centre, rtol=1e-02)
        np.testing.assert_allclose(size, self.cor_rectangle_size, rtol=1e-02)
        np.testing.assert_allclose(angle, self.cor_rectangle_angle, rtol=1e-02)

    def test_cor2_rectangle(self):
        arr = pydicom.read_file(self.COR2_RECTANGLE_PHANTOM_FILE).pixel_array
        shape_detector = hazen_tools.ShapeDetector(arr=arr)
        centre, size, angle = shape_detector.get_shape("rectangle")
        np.testing.assert_allclose(centre, self.cor2_rectangle_centre, rtol=1e-02)
        np.testing.assert_allclose(size, self.cor2_rectangle_size, rtol=1e-02)
        np.testing.assert_allclose(angle, self.cor2_rectangle_angle, rtol=1e-02)


class Test_is_Dicom_file(unittest.TestCase):
    def setUp(self) -> None:
        data_folder = str(TEST_DATA_DIR / "tools")
        self.true_dicom_path = os.path.join(data_folder, "dicom_yes.dcm")
        self.false_dicom_path = os.path.join(data_folder, "dicom_no.jfif")

    def test_is_dicom(self):
        result = hazen_tools.is_dicom_file(self.true_dicom_path)
        self.assertTrue(result)

        result = hazen_tools.is_dicom_file(self.false_dicom_path)
        self.assertFalse(result)

    def test_is_dicom_yes(self):
        result = hazen_tools.is_dicom_file(self.true_dicom_path)
        self.assertTrue(result)

    def test_is_dicom_no(self):
        result = hazen_tools.is_dicom_file(self.false_dicom_path)
        self.assertFalse(result)


class TestUtils(unittest.TestCase):
    def setUp(self):
        TEST_DICOM = str(TEST_DATA_DIR / "toshiba" / "TOSHIBA_TM_MR_DCM_V3_0.dcm")
        TEST_DICOM = pydicom.read_file(TEST_DICOM)
        print(TEST_DICOM.Columns * TEST_DICOM.PixelSpacing[0])
        self.test_dicoms = {
            "philips": {
                "file": str(
                    TEST_DATA_DIR / "resolution" / "philips" / "IM-0004-0002.dcm"
                ),
                "MANUFACTURER": "philips",
                "ROWS": 512,
                "COLUMNS": 512,
                "TR_CHECK": 500,
                "BW": 205.0,
                "ENHANCED": False,
                "PIX_ARRAY": 1,
                "SLICE_THICKNESS": 5,
                "PIX_SIZE": [0.48828125, 0.48828125],
                "AVERAGE": 1,
            },
            "siemens": {
                "file": str(
                    TEST_DATA_DIR / "resolution" / "resolution_site01" / "256_sag.IMA"
                ),
                "MANUFACTURER": "siemens",
                "ROWS": 256,
                "COLUMNS": 256,
                "TR_CHECK": 500,
                "BW": 130.0,
                "ENHANCED": False,
                "PIX_ARRAY": 1,
                "SLICE_THICKNESS": 5,
                "PIX_SIZE": [0.9765625, 0.9765625],
                "AVERAGE": 1,
            },
            "toshiba": {
                "file": str(TEST_DATA_DIR / "toshiba" / "TOSHIBA_TM_MR_DCM_V3_0.dcm"),
                "MANUFACTURER": "toshiba",
                "ROWS": 256,
                "COLUMNS": 256,
                "TR_CHECK": 45.0,
                "BW": 244.0,
                "ENHANCED": False,
                "PIX_ARRAY": 1,
                "SLICE_THICKNESS": 6,
                "PIX_SIZE": [1.0, 1.0],
                "AVERAGE": 1,
            },
            "ge": {
                "file": str(TEST_DATA_DIR / "ge" / "ge_eFilm.dcm"),
                "MANUFACTURER": "ge",
                "ROWS": 256,
                "COLUMNS": 256,
                "TR_CHECK": 1000.0,
                "BW": 156.25,
                "ENHANCED": False,
                "PIX_ARRAY": 1,
                "SLICE_THICKNESS": 5,
                "PIX_SIZE": [0.625, 0.625],
                "AVERAGE": 1,
            },
        }

    def test_is_enhanced(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                enhanced = hazen_tools.is_enhanced_dicom(dcm)
                assert enhanced == self.test_dicoms[manufacturer]["ENHANCED"]

    def test_get_manufacturer(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                assert (
                    hazen_tools.get_manufacturer(dcm)
                    == self.test_dicoms[manufacturer]["MANUFACTURER"]
                )

    def get_average(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                avg = hazen_tools.get_average(dcm)
                assert avg == self.test_dicoms[manufacturer]["AVERAGE"]

    def test_get_bandwidth(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                bw = hazen_tools.get_bandwidth(dcm)
                assert bw == self.test_dicoms[manufacturer]["BW"]

    def test_get_num_of_frames(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                pix_arr = hazen_tools.get_num_of_frames(dcm)
                assert pix_arr == self.test_dicoms[manufacturer]["PIX_ARRAY"]

    def test_get_slice_thickness(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                slice_thick = hazen_tools.get_slice_thickness(dcm)
                assert slice_thick == self.test_dicoms[manufacturer]["SLICE_THICKNESS"]

    def get_pixel_size(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                pix_size = hazen_tools.get_pixel_size(dcm)
                pix_size = list(pix_size)
                self.assertEqual(pix_size, self.test_dicoms[manufacturer]["PIX_SIZE"])

    def test_get_TR(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                TR = hazen_tools.get_TR(dcm)
                assert TR == self.test_dicoms[manufacturer]["TR_CHECK"]

    def test_get_rows(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                rows = hazen_tools.get_rows(dcm)
                assert rows == self.test_dicoms[manufacturer]["ROWS"]

    def test_get_columns(self):
        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                columns = hazen_tools.get_columns(dcm)
                assert columns == self.test_dicoms[manufacturer]["COLUMNS"]

    def test_fov(self):
        self.test_dicoms = {
            "philips": {
                "file": str(
                    TEST_DATA_DIR / "resolution" / "philips" / "IM-0004-0002.dcm"
                ),
                "MANUFACTURER": "philips",
                "FOV": 250.0,
            },
            "siemens": {
                "file": str(
                    TEST_DATA_DIR / "resolution" / "resolution_site01" / "256_sag.IMA"
                ),
                "MANUFACTURER": "siemens",
                "FOV": 250.0,
            },
            "toshiba": {
                "file": str(TEST_DATA_DIR / "toshiba" / "TOSHIBA_TM_MR_DCM_V3_0.dcm"),
                "MANUFACTURER": "toshiba",
                "FOV": 256.0,
            },
        }

        for manufacturer in self.test_dicoms.keys():
            with pydicom.read_file(self.test_dicoms[manufacturer]["file"]) as dcm:
                # first test function
                fov = hazen_tools.get_field_of_view(dcm)
                print(fov)
                assert fov == self.test_dicoms[manufacturer]["FOV"]

    # def test_get_image_orientation(self):
    #     # TODO add unit test for image orientation

    def test_rescale_to_byte(self):
        test_array = np.array([[1, 2], [3, 4]])
        TEST_OUT = np.array([[63, 127], [191, 255]])
        test_array = hazen_tools.rescale_to_byte(test_array)
        test_array = test_array.tolist()
        TEST_OUT = TEST_OUT.tolist()
        self.assertListEqual(test_array, TEST_OUT)

class TestMedACRAnalysis(unittest.TestCase):
    def test_01_Check_MedACRAnalysisRunAllDefault(self):

        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)

        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_AllRun_Default.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_02_Check_MedACRAnalysisRunSNR(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=True, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SNR.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)
        
    def test_03_Check_MedACRAnalysisGeoAcc_MagNet(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=True, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_GeoAccMagNet.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_04_Check_MedACRAnalysisGeoAcc_ACRMethod(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=True, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_GeoAccACRMethod.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_05_Check_MedACRAnalysis_Uniformity(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=True, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_Uniformity.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_06_Check_MedACRAnalysis_Ghosting(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=True, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_Ghosting.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_07_Check_MedACRAnalysis_SlicePos(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=True, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SlicePos.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_08_Check_MedACRAnalysis_SliceThickness(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=True)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SliceThickness.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_09_Check_MedACRAnalysis_SpatialRes_ContrastResponse(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SpatialRes_Contrast.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)


    def test_10_Check_MedACRAnalysis_SpatialRes_DotMatrix(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.DotMatrixMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SpatialRes_DotMatrix.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_11_Check_MedACRAnalysis_SpatialRes_MTF(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.MTFMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)


        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SpatialRes_MTF.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)

    def test_12_Check_MedACRAnalysis_SpatialRes_Manual(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.Manual
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.ACRMETHOD

        #Load in Manual Res
        
        VarHolder = VariableHolder.VarHolder()
        ManualResData = np.load(os.path.join(TEST_DATA_DIR,"MedACR","manualres.npy"),allow_pickle=True).item()
        for key in ManualResData.keys():
            ManualRes = VariableHolder.ManualResData()
            ManualRes.ChosenPointsXPeaks = ManualResData[key][0]
            ManualRes.ChosenPointsYPeaks = ManualResData[key][1]
            ManualRes.ChosenPointsXTroughs = ManualResData[key][2]
            ManualRes.ChosenPointsYTroughs = ManualResData[key][3]
            ManualRes.HoleSize = ManualResData[key][4]
            ManualRes.Image = ManualResData[key][5]

            VarHolder.ManualResData[key] = ManualRes

        MedACRAnalysis.ManualResData = VarHolder.ManualResData
        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=True)
        

        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_SpatialRes_Manual.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)


    def test_13_Check_MedACRAnalysis_TestOverrides(self):
        ACR_DATA_Med = pathlib.Path(TEST_DATA_DIR / "MedACR")

        MedACR_ToleranceTableChecker.SetUpToleranceTable()
        MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
        MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.ManualResData = None

        OverRideData =np.load(os.path.join(TEST_DATA_DIR,"MedACR", "Override.npz"),allow_pickle=True)

        MedACRAnalysis.ParamaterOverides = MedACRAnalysis.ParamaterOveride()

        MedACRAnalysis.ParamaterOverides.CentreOverride = list(OverRideData["arr_0"])
        MedACRAnalysis.ParamaterOverides.RadiusOverride = OverRideData["arr_1"]
        MedACRAnalysis.ParamaterOverides.MaskingOverride = OverRideData["arr_2"]
        MedACRAnalysis.ParamaterOverides.ROIOverride = [OverRideData["arr_3"],OverRideData["arr_4"],OverRideData["arr_5"],OverRideData["arr_6"]]


        MedACRAnalysis.RunAnalysis("ACR AxT1",ACR_DATA_Med,pathlib.PurePath.joinpath(TEST_REPORT_DIR),RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)

        f =open(os.path.join(TEST_DATA_DIR,"MedACR", "Results_Overides.txt"),"r")
        Expectedlines = f.readlines()[3:]
        f.close()

        most_recent_file = max(TEST_REPORT_DIR.glob("*.txt"), key=os.path.getmtime)
        f =open(most_recent_file,"r")
        Outputlines = f.readlines()[3:]
        f.close()

        self.assertListEqual(Expectedlines,Outputlines)
    
if __name__ == "__main__":
    unittest.main()
