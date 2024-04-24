import sys
sys.path.append(".")
import MedACRAnalysis
from hazenlib.utils import get_dicom_files
import pydicom
import glob
import shutil
import os

#Get a list of all sequences for batch testing
files = get_dicom_files("MedACRTesting/TestData/ACR_Phantom_Data")
sequences = []
for file in files:
    data = pydicom.dcmread(file)
    if "Loc" not in data.SeriesDescription and "loc" not in data.SeriesDescription:
        sequences.append(data.SeriesDescription)
    
sequences= list(set(sequences))
print(sequences)
OuptutFolder = "OutputFolder"


inputdata = "MedACRTesting/TestData/ACR_Phantom_Data"
ChosenSeq = "ACR AxT2"


#CLear the output folder so i dont need to do it everytime
#if os.path.exists(OuptutFolder)==True:
#    shutil.rmtree(OuptutFolder)

MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=False, RunSNR=True, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)

