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

files = get_dicom_files("C:\\Users\Johnt\Desktop\QBody_ACR_T1_TRA\YPYDHQGD\JCSDNEGS")
seq = "QBody_ACR_SE_T1_TRA"
ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenData = ACRDICOMSFiles[seq]


ReportDirPath = "C:\\Users\Johnt\Desktop\OutputTest"
acr_uniformity_task = ACRUniformity(input_data=ChosenData,report_dir=ReportDirPath,MediumACRPhantom=True,report=True)
UniformityResult=acr_uniformity_task.run()