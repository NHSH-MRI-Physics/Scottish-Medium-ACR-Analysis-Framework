class DICOMSet:
  
  def __init__(self,DICOM,path):
    self.params = self.__GetParamDict(DICOM)
    self.DICOM_Data = [DICOM]  # Store the first DICOM in the set
    self.paths = [path]

  def __GetParamDict (self,DICOM):
    return {
      "EchoTime": DICOM.EchoTime,
      "RepetitionTime": DICOM.RepetitionTime,
      "SeriesDescription": DICOM.SeriesDescription,
      "SeriesInstanceUID": DICOM.SeriesInstanceUID,
      "SliceThickness": DICOM.SliceThickness,
      "Matrix": str(DICOM.Rows)+","+ str(DICOM.Columns),
      "PixelSpacing": str(DICOM.PixelSpacing[0]) +"," + str(DICOM.PixelSpacing[1]),
      "Bandwidth": DICOM.PixelBandwidth
    }

  def Does_DICOM_Match(self,DICOM):
    Test_Params = self.__GetParamDict(DICOM)
    MatchCount = 0
    for key in self.params:
        if self.params[key] == Test_Params[key]:
            MatchCount+=1
    return MatchCount == len(self.params)  # All parameters must match
  
  def AddDICOM (self,DICOM,file):
    if self.Does_DICOM_Match(DICOM) == False:
      raise ValueError("DICOM does not match existing DICOMs in this set.") #Kinda dont need the above fucntion but it is useful for debugging
    self.DICOM_Data.append(DICOM)
    self.paths.append(file)