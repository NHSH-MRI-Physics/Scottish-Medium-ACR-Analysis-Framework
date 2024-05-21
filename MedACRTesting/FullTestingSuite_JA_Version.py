import sys
sys.path.append(".")
import MedACRAnalysis
from hazenlib.utils import get_dicom_files
import pydicom
import glob
import shutil
import os


OuptutFolder = "OutputFolder"
inputdata = "MedACRTesting/TestData/ACR_Phantom_Data"
ChosenSeq = "ACR AxT1"
MedACRAnalysis.RunAnalysis(ChosenSeq,inputdata,OuptutFolder,RunAll=True, RunSNR=False, RunGeoAcc=False, RunSpatialRes=False, RunUniformity=False, RunGhosting=False, RunSlicePos=False, RunSliceThickness=False)