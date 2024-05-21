import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Hazen-ScottishACR-Fork")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
import pydicom
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_snr import ACRSNR
from hazenlib.tasks.acr_slice_position import ACRSlicePosition
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR


ReportDirPath = "MedACRTests"
#This test needs fixed
#Make sure it works with the test data
'''
files = get_dicom_files("tests\\data\\acr\\GE")
acr_slice_position_task = ACRSlicePosition(input_data=files,report_dir=ReportDirPath,report=True)
dcm_1 = acr_slice_position_task.ACR_obj.dcms[0]
dcm_11 = acr_slice_position_task.ACR_obj.dcms[-1]
slice1pos = acr_slice_position_task.get_slice_position(dcm_1)
slice11pos = acr_slice_position_task.get_slice_position(dcm_11)
print(slice1pos,slice11pos)
'''

files = get_dicom_files("ACR_MRI1_20240116_104902641")
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenData = ACRDICOMSFiles["ACR AxT1"]

#Test SNR
#Only change neede was the paramaters of the hough circles
acr_slice_position_task = ACRSlicePosition(input_data=ChosenData,report_dir=ReportDirPath,report=True,MediumACRPhantom=True)
dcm_1 = acr_slice_position_task.ACR_obj.dcms[0]
dcm_11 = acr_slice_position_task.ACR_obj.dcms[-1]
slice1pos = acr_slice_position_task.get_slice_position(dcm_1)
slice11pos = acr_slice_position_task.get_slice_position(dcm_11)
#print(slice1pos,slice11pos)