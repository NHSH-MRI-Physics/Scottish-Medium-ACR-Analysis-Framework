import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Scottish-Medium-ACR-Analysis-Framework")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
import pydicom
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_cnr import ACRCNR
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR

OutputPath = "C:\\Users\\Johnt\\Documents\\GitHub\\Scottish-Medium-ACR-Analysis-Framework\\OutputFolder"
Data = get_dicom_files("C:\\Users\\Johnt\\Documents\\GitHub\\Scottish-Medium-ACR-Analysis-Framework\\MedACRTestingSetAndResults\\Forth Valley ACR Blair T1")
x=0

acr_cnr_task = ACRCNR(input_data=Data, report_dir=OutputPath,report=True,MediumACRPhantom=True)
results = acr_cnr_task.run()
