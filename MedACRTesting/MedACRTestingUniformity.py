import pydicom
import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Hazen-ScottishACR-Fork")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_snr import ACRSNR
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR

ReportDirPath = "MedACRTests"
'''
#Make sure it works with the test data
ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "Siemens")
ChosenData = get_dicom_files(ACR_DATA_SIEMENS)
acr_uniformity_task = ACRUniformity(input_data=ChosenData,report_dir=ReportDirPath,report=True)
Uniformity = acr_uniformity_task.get_integral_uniformity(acr_uniformity_task.ACR_obj.slice7_dcm)
'''

files = get_dicom_files("ACR_MRI1_20240116_104902641")
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenData = ACRDICOMSFiles["ACR AxT1"]


acr_uniformity_task = ACRUniformity(input_data=ChosenData,report_dir=ReportDirPath,MediumACRPhantom=True,report=True)
Uniformity = acr_uniformity_task.get_integral_uniformity(acr_uniformity_task.ACR_obj.slice7_dcm)
print(Uniformity)