import sys
sys.path.append(".")
import MedACRAnalysis
from hazenlib.utils import get_dicom_files
import pydicom
import glob
import shutil
import os

inputdata = "MedACRTesting/TestData/ACR_Phantom_Data"
#inputdata = "C:\\Users\Johnt\Desktop\IM_0043"

#Get a list of all sequences for batch testing
files = get_dicom_files(inputdata)
sequences = []
for file in files:
    data = pydicom.dcmread(file)
    if "Loc" not in data.SeriesDescription and "loc" not in data.SeriesDescription:
        sequences.append(data.SeriesDescription)
    
sequences= list(set(sequences))
print(sequences)
OuptutFolder = "OutputFolder"

#CLear the output folder so i dont need to do it everytime
#if os.path.exists(OuptutFolder)==True:
#    shutil.rmtree(OuptutFolder)
ChosenSeq = "ACR AxT2"
#ChosenSeq = "ACR_ax_T1" #"ACR AxT2"
MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)