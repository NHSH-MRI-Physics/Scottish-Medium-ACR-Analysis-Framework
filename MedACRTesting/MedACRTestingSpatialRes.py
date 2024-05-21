import pydicom
import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Hazen-ScottishACR-Fork")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_snr import ACRSNR
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR

ReportDirPath = "MedACRTests"

ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "SiemensMTF")
ChosenFiles = get_dicom_files(ACR_DATA_SIEMENS)
acr_spatial_resolution_task = ACRSpatialResolution(input_data=ChosenFiles,report_dir=ReportDirPath,report=True)
dcm = acr_spatial_resolution_task.ACR_obj.dcms[0]
mtf50 = acr_spatial_resolution_task.get_mtf50(dcm)
print(mtf50)


files = get_dicom_files("ACR_MRI1_20240116_104902641")
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenFiles = ACRDICOMSFiles["ACR AxT1"]

acr_spatial_resolution_task = ACRSpatialResolution(input_data=ChosenFiles,report_dir=ReportDirPath,report=True,MediumACRPhantom=True)
dcm = acr_spatial_resolution_task.ACR_obj.dcms[0]
mtf50 = acr_spatial_resolution_task.get_mtf50(dcm)
print(mtf50)
