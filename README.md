![bitmap](https://github.com/user-attachments/assets/e2396cbd-39a0-4213-afdb-64e92b88db04)![image](https://github.com/user-attachments/assets/032f9caf-3bcf-4d5c-8767-4617c70a7bba)![Med_ACR_Tra_T2_8001_7](https://github.com/user-attachments/assets/9be40afe-aa31-4ba7-a4bc-dd2f7336b526)![example workflow](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/actions/workflows/Run_UnitTests.yml/badge.svg)

Version: Pre-Release

### Devlopment branch for the medium ACR Phantom QA project. 
Please note this project is currently a work in progress, dervived from the [Hazen MRI QA framework](https://github.com/GSTT-CSC/hazen). The documentation and project is incpomplete, the code is messy and bugs will almost certainly be present. If any bugs or issues are found please raise an [issue](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/issues) within github. 
## Current Status and To Do
- [x] Add medium ACR phantom compatibility to the Hazen code base.
- [x] Incorporate docker image of the Hazen code base with medium ACR compatibility.
- [x] Build GUI for the medium ACR phantom implementation.
- [x] Build a version of the GUI which does not require internet connection (to update Docker image).
- [x] Make a release package
- [x] Build unit tests.
- [ ] Write documentation.
- [ ] get baseline values from a series of scanners

## Instalation, Set up and Quickstart

## Requiremenets 
- Windows (Mac and Linux coming soon)
## Installation
- Download the latest [release](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/releases/latest).
- Unzip the file and navigate to where it was downloaded.
## Quick Start
- Double click and start ACR QA Analysis.exe.
- Select the location of the DICOM folder using the "Set DICOM Path" button.
- Select where the results will be outputted to usign the "Set Results Output Path" button.
- Select what sequence to analyse using the dropdown.
- Select whats tests you want to run from the checkboxes.
- Click "Start Analysis"
- On completion the results are displaeyd and you can view individual results by selecting the dropdown (below the "Start Analysis" button) following the "View Results" button.

![bitmap](https://github.com/user-attachments/assets/d980cfdd-2142-46ae-942e-a1e206b8ac48)


## Expected Data Format
it is expected to be a directory containing DICOM files, where each file coresponds to one slice, it is possible to have several sequeunces contained within the folder. Data should be collected as laid out in the [ACR Large and medium guidance document](https://www.acraccreditation.org/-/media/ACRAccreditation/Documents/MRI/ACR-Large--Med-Phantom-Guidance-102022.pdf). If it is desired to test sagittal and coronal axis, this is possible by rotating the phantom appropriately. It is important that the phantom or field of view is rotated such that circular component as at the top of the image and the resolution block is located at the bottom regardless if you are imaging axial, sagittal or coronal.  See the Image below for an example. 

![image](https://github.com/user-attachments/assets/df2a6626-892f-44e3-8fef-5d1766ddf014)

## Testing Protocol 



## Developers
John Tracey NHS Highland (John.tracey@NHS.scot)
Hamish Richardson NHS Lothian (hamish.richardson@nhs.scot)
