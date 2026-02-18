from pydicom import dcmread  
import glob
import matplotlib.pyplot as plt
import sys
sys.path.append(".")
from hazenlib.utils import is_enhanced_dicom, get_dicom_files
import numpy
from MedACRModules.SNR_Module import SNRModule


path = "C:\\Users\\John\\Desktop\\Enhanced\\15400000"
files = glob.glob(path + "/*")

for file in files:
    ds = dcmread(file)
    if type(getattr(ds, "pixel_array", None)) == numpy.ndarray:
        
        if ds.NumberOfFrames == 11:
            #print (is_enhanced_dicom(ds))
            print(ds.pixel_array.shape)
            #plt.imshow(ds.pixel_array[0])
            #plt.savefig("test.png")
            #Test = SNRModule("SNR",settings)