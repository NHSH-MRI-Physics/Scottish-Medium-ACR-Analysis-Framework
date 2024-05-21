import pydicom
import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Hazen-ScottishACR-Fork")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_geometric_accuracy import ACRGeometricAccuracy
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR

ReportDirPath = "MedACRTests"
'''
#Make sure it works with the test data
ACR_DATA_SIEMENS = pathlib.Path(TEST_DATA_DIR / "acr" / "Siemens")
ChosenData = get_dicom_files(ACR_DATA_SIEMENS)
acr_geometric_accuracy_task = ACRGeometricAccuracy(input_data=ChosenData,report_dir=ReportDirPath,MediumACRPhantom=False,report=True)
dcm_1 = acr_geometric_accuracy_task.ACR_obj.dcms[0]
dcm_5 = acr_geometric_accuracy_task.ACR_obj.dcms[4]
slice1_vals = acr_geometric_accuracy_task.get_geometric_accuracy_slice1(dcm_1)
slice5_vals = acr_geometric_accuracy_task.get_geometric_accuracy_slice5(dcm_5)
print(slice1_vals,slice5_vals)
'''

files = get_dicom_files("ACR_MRI1_20240116_104902641")
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenData = ACRDICOMSFiles["ACR AxT1"]

acr_geometric_accuracy_task = ACRGeometricAccuracy(input_data=ChosenData,report_dir=ReportDirPath,MediumACRPhantom=True,report=True)
dcm_1 = acr_geometric_accuracy_task.ACR_obj.dcms[0]
dcm_5 = acr_geometric_accuracy_task.ACR_obj.dcms[4]
slice1_vals = acr_geometric_accuracy_task.get_geometric_accuracy_slice1(dcm_1)
slice5_vals = acr_geometric_accuracy_task.get_geometric_accuracy_slice5(dcm_5)
print(slice1_vals,slice5_vals)