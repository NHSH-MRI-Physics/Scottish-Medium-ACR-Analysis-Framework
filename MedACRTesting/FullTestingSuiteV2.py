import sys
sys.path.append(".")
import MedACRAnalysis
from hazenlib.utils import get_dicom_files
import pydicom
import glob
import shutil
import os
import MedACROptions
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
inputdata = "C:\\Users\John\Desktop\ACR Blair T1"
inputdata = "C:\\Users\John\Desktop\Raigmore ACR MRI 2 Test data"

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
ChosenSeq = "ACR_Axial_T1"
ChosenSeq = "Ax T1 SE"
#ChosenSeq = "ACR_ax_T1" #"ACR AxT2"

MedACR_ToleranceTableChecker.SetUpToleranceTable()
MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD
MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=True, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)