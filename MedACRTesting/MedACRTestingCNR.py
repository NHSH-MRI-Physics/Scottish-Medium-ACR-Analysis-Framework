

import sys
sys.path.insert(0,"C:\\Users\\Johnt\\Documents\\GitHub\\Scottish-Medium-ACR-Analysis-Framework")
sys.path.insert(0,"D:\\Hazen-ScottishACR-Fork")
from hazenlib.utils import get_dicom_files
from hazenlib.tasks.acr_cnr import ACRCNR
from hazenlib.tasks.acr_uniformity import ACRUniformity
from hazenlib.ACRObject import ACRObject
import pathlib
from tests import TEST_DATA_DIR, TEST_REPORT_DIR

import SimpleITK as sitk
import matplotlib.pyplot as plt
import pydicom

OutputPath = "OutputFolder"
Data = get_dicom_files("MedACRTestingSetAndResults\\Blair Gartnavel")
#x=0

acr_cnr_task = ACRCNR(input_data=Data, report_dir=OutputPath,report=True,MediumACRPhantom=True)
results = acr_cnr_task.run()


sys.exit()
#Get a 2d image
ref3d = sitk.ReadImage("_internal\\StandardDicom\\I1100000")
input3d = sitk.ReadImage("MedACRTestingSetAndResults\Blair Gartnavel\IM_0048")

extract = sitk.ExtractImageFilter()
extract.SetSize([ref3d.GetSize()[0], ref3d.GetSize()[1], 0])
extract.SetIndex([0, 0, 0])
fixed = extract.Execute(ref3d)

extract = sitk.ExtractImageFilter()
extract.SetSize([input3d.GetSize()[0], input3d.GetSize()[1], 0])
extract.SetIndex([0, 0, 0])
moving = extract.Execute(input3d)

#Reset the origins to (0,0) to avoid any issues with the registration
moving.SetOrigin((0.0, 0.0))
fixed.SetOrigin((0.0, 0.0))

print("fixed origin:", fixed.GetOrigin())
print("fixed spacing:", fixed.GetSpacing())
print("fixed direction:", fixed.GetDirection())

print("moving origin:", moving.GetOrigin())
print("moving spacing:", moving.GetSpacing())
print("moving direction:", moving.GetDirection())


refimage = sitk.Cast(fixed, sitk.sitkFloat32)
inputimage = sitk.Cast(moving, sitk.sitkFloat32)

elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(refimage)
elastixImageFilter.SetMovingImage(inputimage)
elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("affine"))
elastixImageFilter.Execute()
result = elastixImageFilter.GetResultImage()


RefPhys = [130.86,116.22]#In phys space in mm
RefIdx = refimage.TransformPhysicalPointToIndex(RefPhys)


fixed_array = sitk.GetArrayFromImage(refimage)
moving_array = sitk.GetArrayFromImage(inputimage)
result_array = sitk.GetArrayFromImage(result)

fig, axs = plt.subplots(1, 3, figsize=(15, 5))
axs[0].imshow(fixed_array, cmap="gray"); axs[0].set_title("Fixed (this is the reference image)"); axs[0].axis("off")
axs[0].plot(RefIdx[0], RefIdx[1], 'rx')  # Plot the test point on the moving image
axs[1].imshow(moving_array, cmap="gray"); axs[1].set_title("Moving (this is our input image)"); axs[1].axis("off")
axs[2].imshow(fixed_array, cmap="gray")
axs[2].imshow(result_array, cmap="Blues", alpha=0.3)
axs[2].plot(RefIdx[0], RefIdx[1], 'rx')  # Plot the test point on the moving image
plt.savefig("test2.png",dpi=300)