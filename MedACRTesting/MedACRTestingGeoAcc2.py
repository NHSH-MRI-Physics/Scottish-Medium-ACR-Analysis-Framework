#import matplotlib.pyplot as plt
import pydicom
#import pydicom.data
import sys
sys.path.insert(0,"F:\\Medical Physics\\DMP\\RPIP\\Imaging\\MRI\\QA\\Hazen-MediumACRPhantom")
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_geometric_accuracy2 import ACRGeometricAccuracy2
from hazenlib.tasks.slice_width import SliceWidth
from hazenlib.ACRObject import ACRObject
from pathlib import Path
#from tests import TEST_DATA_DIR, TEST_REPORT_DIR
from tkinter import filedialog as fd

file1 = "MR.X.1.2.276.0.7230010.3.1.4.0.1432.1705402143.704839.dcm"  # file name is 1-12.dcm 
ReportDirPath = "Results" 

# File-selector for Unit-Testing:
folder_sel = fd.askdirectory()
files = get_dicom_files(folder_sel,sort=False)
path=Path(folder_sel)
parent_directory=path.parent.parent.absolute()
#file_sel=fd.askopenfilename()
#print(folder_sel)

ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
ChosenData = ACRDICOMSFiles[data.SeriesDescription]
#plt.imshow(data.pixel_array, cmap=plt.cm.bone)  # set the color map to bone 
#plt.show() 
#print(f"Chosendata = {ChosenData}")


#Try calculating distortion on the rods using the MagNET code

acr_geometric_accuracy_task = ACRGeometricAccuracy2(input_data=ChosenData,report_dir=parent_directory,MediumACRPhantom=True,report=True)
dcm_5 = acr_geometric_accuracy_task.ACR_obj.dcms[4]
arr=dcm_5.pixel_array
rods, rods_initial = acr_geometric_accuracy_task.get_rods(arr)
horz_distances, vert_distances, horz_dist_mm, vert_dist_mm = acr_geometric_accuracy_task.get_rod_distances(rods)
horz_distortion_mm, vert_distortion_mm = acr_geometric_accuracy_task.get_rod_distortions(
horz_dist_mm, vert_dist_mm
)
#slice5_vals=acr_geometric_accuracy_task.get_rod_distortions(120,120)
#slice5_vals=self.get_rod_distortions(120,120)
print(f'Results for series {data.SeriesDescription}: Horizontal Distortion= {horz_distortion_mm}, Vertical Distortion={vert_distortion_mm}')
print(f'Horz-Top = {horz_dist_mm[0]}')
print(f'Horz-Middle = {horz_dist_mm[1]}')
print(f'Horz-Bottom = {horz_dist_mm[2]}')
print(f'Vert-Left= {vert_dist_mm[0]}')
print(f'Vert-Middle= {vert_dist_mm[1]}')
print(f'Vert-Right= {vert_dist_mm[2]}')