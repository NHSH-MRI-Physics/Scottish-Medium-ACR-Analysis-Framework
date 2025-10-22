import sys
sys.path.append(".")
from MedACROptions import *
import PyInstallerGUI.VariableHolder

class DICOMParamaters:
    def __init__(self):
        self.MatrixFreq = None
        self.MatrixPhase = None
        self.TE = None
        self.TR = None
        self.PixelSpacingRow = None
        self.PixelSpacingCol = None
        self.SliceThickness = None
        self.Averages = None
        self.SequenceType = None
        self.SliceGap = None
        self.Slices = None
        self.GeoDistMethod = None
        self.UniformityMethod = None
        self.SpaitalResMethod = None


    def CompareParamaters(self,DICOM):
        ComparisonDataBase = {}
        Variables = vars(self).keys()
        AllPassed = True
        for var in Variables:
            ComparisonDataBase[var] = [vars(self)[var],vars(DICOM)[var],True]
            if vars(self)[var] != vars(DICOM)[var]:
                AllPassed = False
                ComparisonDataBase[var][-1] = False
                #return False, var+" Mismatch Standard=" +str(vars(self)[var]) + " vs DICOM=" + str(vars(DICOM)[var])
        return AllPassed, ComparisonDataBase

StandardParamT1 = DICOMParamaters()
StandardParamT1.MatrixFreq = 256
StandardParamT1.MatrixPhase = 256
StandardParamT1.TE = 20
StandardParamT1.TR = 500
StandardParamT1.Slices = 11
StandardParamT1.SliceThickness = 5
StandardParamT1.SliceGap = 5
StandardParamT1.Averages = 1
StandardParamT1.SequenceType = "SE"
StandardParamT1.PixelSpacingCol = 0.977
StandardParamT1.PixelSpacingRow = 0.977
StandardParamT1.GeoDistMethod = "ACRGeometricAccuracyMagNetMethod"
StandardParamT1.UniformityMethod = UniformityOptions.ACRMETHOD
StandardParamT1.SpaitalResMethod = "ContrastResponse"

StandardParamT2 = DICOMParamaters()
StandardParamT2.MatrixFreq = 256
StandardParamT2.MatrixPhase = 256
StandardParamT2.TE = 80
StandardParamT2.TR = 2000
StandardParamT2.Slices = 11
StandardParamT2.SliceThickness = 5
StandardParamT2.SliceGap = 5
StandardParamT2.Averages = 1
StandardParamT2.SequenceType = "SE"
StandardParamT2.PixelSpacingCol = 0.977
StandardParamT2.PixelSpacingRow = 0.977
StandardParamT2.GeoDistMethod = "ACRGeometricAccuracyMagNetMethod"
StandardParamT2.SpaitalResMethod = "ContrastResponse"

def CheckAgainstStandard(BinaryFile):
    Slices = len(BinaryFile["DICOM"])
    for dcm in BinaryFile["DICOM"]:
        PhaseEncodingDir = dcm.InPlanePhaseEncodingDirection
        Matrix = dcm.AcquisitionMatrix
        TE = dcm.EchoTime
        TR = dcm.RepetitionTime
        PixelSpacing = dcm.PixelSpacing
        SliceThickness = dcm.SliceThickness
        Averages = dcm.NumberOfAverages
        SequenceType = dcm.ScanningSequence
        SliceGap = dcm.SpacingBetweenSlices

        DICOM_Param_Obj = DICOMParamaters()
        DICOM_Param_Obj.TE = round(TE,3)
        DICOM_Param_Obj.TR = round(TR,3)
        DICOM_Param_Obj.PixelSpacingRow = round(PixelSpacing[0],3)
        DICOM_Param_Obj.PixelSpacingCol = round(PixelSpacing[1],3)
        DICOM_Param_Obj.SliceThickness = SliceThickness
        DICOM_Param_Obj.Averages = Averages
        DICOM_Param_Obj.SequenceType = SequenceType
        DICOM_Param_Obj.SliceGap = SliceGap
        DICOM_Param_Obj.UniformityMethod = BinaryFile["Test"]["Uniformity"].settings["UniformityMethod"]
        if (dcm.Manufacturer) == "GE MEDICAL SYSTEMS" or "Siemens".upper() in dcm.Manufacturer.upper():
            DICOM_Param_Obj.SliceGap = round(SliceGap - SliceThickness,3)
        if PhaseEncodingDir == 'ROW':
            DICOM_Param_Obj.MatrixFreq = Matrix[1]
            DICOM_Param_Obj.MatrixPhase = Matrix[2]
        else:
            DICOM_Param_Obj.MatrixFreq = Matrix[0]
            DICOM_Param_Obj.MatrixPhase = Matrix[3]
        DICOM_Param_Obj.Slices = Slices
        DICOM_Param_Obj.GeoDistMethod = BinaryFile["Test"]["GeoDist"].results["task"]
        DICOM_Param_Obj.SpaitalResMethod = BinaryFile["Test"]["SpatialRes"].settings["SpatialResMethod"]
        if DICOM_Param_Obj.SpaitalResMethod == ResOptions.Manual or DICOM_Param_Obj.SpaitalResMethod == ResOptions.ContrastResponseMethod:
            DICOM_Param_Obj.SpaitalResMethod = "ContrastResponse"

        ComparisonStatus,Data = StandardParamT1.CompareParamaters(DICOM_Param_Obj)
        if ComparisonStatus == False:
            return False,Data
    return True, Data