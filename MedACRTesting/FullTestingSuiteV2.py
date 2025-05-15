import sys
sys.path.append(".")
#import MedACRAnalysis
import MedACRAnalysisV2 as MedACRAnalysis
from hazenlib.utils import get_dicom_files
import pydicom
import glob
import shutil
import os
import MedACROptions
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker

inputdata = "MedACRTestingSetAndResults\Blair Gartnavel"
ChosenSeq="ACR_ax_T1"

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



MedACR_ToleranceTableChecker.SetUpToleranceTable()
MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD


MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=False , RunSNR=True, RunGeoAcc=True, RunSpatialRes=True, RunUniformity=True, RunGhosting=True, RunSlicePos=True, RunSliceThickness=True)