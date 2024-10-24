![UnitTests](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/actions/workflows/Run_UnitTests.yml/badge.svg)

Version: Pre-Release v1.01
### Scottish Medium ACR Phantom QA project. 
![SplashScreen](https://github.com/user-attachments/assets/85599d11-94d9-49e3-8795-e07fd0eb35e3)


Derived from the [Hazen MRI QA framework](https://github.com/GSTT-CSC/hazen) project, this is a extension which is designed to work with the medium ACR phantom. Some other additions have also been made such as the GUI although the framework remains intact with the original hazen project.

## Current Status and To Do
- [x] Add medium ACR phantom compatibility to the Hazen code base.
- [x] Incorporate docker image of the Hazen code base with medium ACR compatibility.
- [x] Build GUI for the medium ACR phantom implementation.
- [x] Build a version of the GUI which does not require internet connection (to update Docker image).
- [x] Make a release package
- [x] Build unit tests.
- [x] Write documentation.
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
- On completion the results are displayed and you can view individual results by selecting the dropdown (below the "Start Analysis" button) following the "View Results" button.

![drawing](https://github.com/user-attachments/assets/97b2042b-d5eb-4004-87e9-da4f027cd4db)


## Scanning Protocol
Scan the ACR Phantom as laid our in the [ACR Large and medium guidance document](https://www.acraccreditation.org/-/media/ACRAccreditation/Documents/MRI/ACR-Large--Med-Phantom-Guidance-102022.pdf). It is possible to scan in other orientations than axial but the phantom must be rotated correctly (see below). It is also possible to use other coils than the head but this has not been fully tested. 

## Expected Data Format
It is expected to be a directory containing DICOM files, where each file coresponds to one slice, it is possible to have several sequeunces contained within the folder. Data should be collected as laid out in the [ACR Large and medium guidance document](https://www.acraccreditation.org/-/media/ACRAccreditation/Documents/MRI/ACR-Large--Med-Phantom-Guidance-102022.pdf). If it is desired to test sagittal and coronal axis, this is possible by rotating the phantom appropriately. It is important that the phantom or field of view is rotated such that circular component as at the top of the image and the resolution block is located at the bottom regardless if you are imaging axial, sagittal or coronal.  See the Image below for an example. 

![image](https://github.com/user-attachments/assets/df2a6626-892f-44e3-8fef-5d1766ddf014)

## Modules
### Uniformity
This is computed by moving a 1cm^2 circular ROI over the phantom and computing the mean pixel value in each region. By considering the maximum and minimum values the percentage uniformity can be determeined. 

### Slice Position
On the ACR Phantom, the slice position can be determined by examining two bars located at the top of the phantom. The difference in the bars height coresponds to the error in slice position. The code produces a line profile over each bar and determines the offset between them. Hence it can compute the slice position error. 

### Spatial Resolution
#### Contrast Response 
On slice 1 there is a series of dot matrices designed to measure resoloution performance. For each grid, this module automatically attempts to determine what row and coloumn in each grid yeilds the highest contrast response. This is repeated for each grid yeilding a contrast response value as a function of grid size.
#### Modulation Transfer Function (MTF)
On slice 1 an edge is found and a line profile extracted over it. This profile is differentated and the fourier transform taken, computing the MTF. For this to be effective the phantom is expected to be rotated by at least 3 degrees. 
#### Manual (Recommended option)
This module displays to the user each resolution grid. The user then has to highlight the peaks and troughs on each grid image. This is conducted by left clicking 4 times to identify the 4 horizontal peaks (blue crosses) and then 3 times to identify the 3 troughs (blue circles). By holding ctrl then left clicking the user can highlight the 4 vertical peaks and 3 vertical troughs in the same fashion as the horizontal component, these are labeled as red crosses and circles. By Pressing Alt, the troughs are automatically assigned based on the middle location between the peaks. The windowing can also be adjusted by right clicking and dragging. By shift-clicking or ctrl-shift-clicking points already placed on the image can be removed. After all 4 resolution grids have been evaluated the contrast response is computed.

### Slice Thickness
The ACR phantom contains two ramps which depending on the slice thickness will appear longer or shorter. The code draws a line over each bar and computes the full width half maximum of the profile. Based on the width of the profile, the slice thickness can be deteremined. 

### Signal to Noise Ratio
Signal to noise ratio is computed by firstly taken the mean pixel value in 5 regions of interest to produce 5 signal values. The image is convoluted with a 9x9 boxcar kernal to produce a smoothed image. The convoluted image is subtracted from the original signal image to produce a noise image. The standard deviation is taken in each region of interest in the noise image. This allows a signal to noise ratio be computed for each region of interest. Finally the mean over all region of interests is computed giving the final result.

### Geometric Accuracy
#### ACR Method
The horizontal and vertical size of the phantom is measured on slice 1. The diagonal, horizontal and vertical size of the phantom is measured on slice 5. These values are then compared with the expected size of the phantom,  
#### MagNET Method (Recommended option)
On slice 5, 9 pegs are used to determine geometric accuracy. The distances between each peg is measured and compared against the expected distance between the pegs.


### Ghosting
A region of interest is placed within the phantom and 4 further are placed above, below, left and right of the phantom. By considering the fraction between the signal in the peripheral regions with that of the centre, the percentage value of ghosting can be deteremined. 

## Tolerance Table
The tolerance table is used to quickly identify if a test is within tolerance. The tolerance table is in the ToleranceTable/ToleranceTable.xml file. In order to add a test to the tolerance table, you must add an XML element called module with the name field set to be the same as the module in question. For each module you can then add test tolerances, a child element is then added named Test. In each element the name field must be set to be equal to the specific test result (for example "1.1mm holes Horizontal").  You can then set a Min, Max or Equals value in this element. If the value is greater than min, lower than max or equal to the tolerance then it is considered within tolerance. If a module or test is not found in the tolerance table, then the script returns "No Tolerance Set". If no name is set on the test element, then the same tolerance is used for every test in that module.

## Testing Protocol 
To confirm the scripts, match expected results a testing protocol was developed. The goal of this was test each module and confirm it meets manual measurements is within a given tolerance. This testing protocol can be found [here](https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/MedACRTestingSetAndResults/Hazen%20Test%20Plan.docx) and the results found [here](https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/MedACRTestingSetAndResults/ACR%20Test%20Document%20%20V1.xlsx). Be sure to click Download Raw File to get the file without downloading the whole repo.

## Bug Reports and Feature Requests
Please make any bug reports or feature requests by logging an issue [here](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/issues) or send an email to the developers below. 

## Developers
John Tracey NHS Highland (John.tracey@nhs.scot)
Hamish Richardson NHS Lothian (hamish.richardson@nhs.scot)
