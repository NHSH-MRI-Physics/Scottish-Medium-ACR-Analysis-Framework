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
inputdata = "C:\\Users\\Johnt\\Desktop\\Artist_ACR_badshim_150225\\Scan1\\ACR_TRA_T1\\QDTQUOWE\\YVRQTPFT"

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
ChosenSeq = "ACR_TRA_T1"


MedACR_ToleranceTableChecker.SetUpToleranceTable()
#MedACRAnalysis.SpatialResMethod=MedACROptions.ResOptions.ContrastResponseMethod
#MedACRAnalysis.GeoMethod=MedACROptions.GeometryOptions.MAGNETMETHOD

#MedACRAnalysis.ParamaterOverides.CentreOverride = [130,130]
#MedACRAnalysis.ParamaterOveride.RadiusOverride = 80

MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=False, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=True)