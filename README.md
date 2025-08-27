![UnitTests](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/actions/workflows/Run_UnitTests.yml/badge.svg)

Version: Pre-Release v1.02
### Scottish Medium ACR Phantom QA project. 
![SplashScreen](https://github.com/user-attachments/assets/85599d11-94d9-49e3-8795-e07fd0eb35e3)


Derived from the [Hazen MRI QA framework](https://github.com/GSTT-CSC/hazen) project, this is a extension which is designed to work with the medium ACR phantom. Some other additions have also been made such as the GUI although the framework remains intact with the original hazen project.

## Current Status and To Do
- [x] Add medium ACR phantom compatibility to the Hazen code base.
- [x] Incorporate docker image of the Hazen code base with medium ACR compatibility.
- [x] Build GUI for the medium ACR phantom implementation.
- [x] Build a version of the GUI which does not require internet connection.
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

![path30](https://github.com/user-attachments/assets/0ef4008e-d647-4fdc-a12a-e94b0dac3a79)



## Scanning Protocol
Scan the ACR Phantom as laid our in the [ACR Large and medium guidance document]([https://www.acraccreditation.org/-/media/ACRAccreditation/Documents/MRI/ACR-Large--Med-Phantom-Guidance-102022.pdf](https://acrsupport.attachments3.freshdesk.com/data/helpdesk/attachments/production/11093487417/original/MR%20ACR%20Large%20%20Med%20Phantom%20Guidance%20102022.pdf?response-content-type=application%2Fpdf&Expires=1756309225&Signature=MK9DXu23EWaZbObrruB9cB4prLqEYx9tEOvNQo~jfPmBycYBi5dIX3dbR2Tt8D7dRecUhb3TIuzh8kIYjnJVNH-KFmitEV0Bb775bvKbkUfHItSmZSqGfe2Z2KA5OFt9xaEFI~~VsPGkEE~sRsmHFkw7eZxf04qBSyfyM1YMBYEskVISmx98ZjvwtU1cDBWucCFbxNcXfiNy~3TfSqHlDezsFM8VFI9QznnqmpHFPG5HEHOCm7jqoh~KFUQ2upxxONp452Ow~XCrmQQKdLKsuMy42CTCwjmgKaeelGweFQbmfxeAfJ8TosJaNcru6UtZikFMB8RMFPV8B2Z5q4nx2w__&Key-Pair-Id=APKAJ7JARUX3F6RQIXLA)). It is possible to scan in other orientations than axial but the phantom must be rotated correctly (see below). It is also possible to use other coils than the head but this has not been fully tested. 

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
On slice 1 there is a series of dot matrices designed to measure resoloution performance. For each grid, this module automatically attempts to determine what row and coloumn in each grid yeilds the highest contrast response. This is repeated for each grid yeilding a contrast response value as a function of grid size. For more information refer to [here](https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/docs/ContrastResponse.md)
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

### Manual Overrides
In some instances the algorithms which find the phantom centre, mask or the resolution blocks may fail or be inaccurate. It is possible to manually override these factors, these options can be found by clicking "Open Options". Please note depending on the moodule, several slices may need to be overridden.

#### Override Radius and Centre 
The centre and radius of the phantom is used in various modules. By selecting this option the radius and centre of the phantom is computed from the manual override. When this option is selected one or several (depending on what modules are selected are shown) is displayed. Left click on the perimitter 4 times at the top, bottom, left and right of the phantom. A circle is fitted to these points and is displayed as a red line, the phantom centre and radius is computed based on this fitted circle and used in future calculations. If alterations are wished to be made, right clicking on each point will delete them allowing you to replace them. Please note, at the bottom of the image there is an option to zoom in which will help with accurate marking. 

![image](https://github.com/user-attachments/assets/31b1da0c-4159-464e-a6de-999e12f57f98)

#### Override Masking
Some modules require a binary mask of the phantom, this is usually computed based on a thresholding method. This on occasion can fail, hence can be manually overridden. The process is identical to the "Override Radius and Centre" described above. Although in this case the fitted circle is used to determine the location of the binary mask used in modules. The mask can be viewed as a yellow shaded region.

![image](https://github.com/user-attachments/assets/98afa201-f070-4e23-a93c-63fed9e447a4)

#### Override Res Blocks Location
Most of the spatial resolution algorithms try to find the position of the four sets of resolution grids located in the ACR phantom, for various reasons the algorithm may struggle to find these. Hence, the location of these can be overridden. To do this, simply draw 4 rectangles (by left clicking) which surround each of the 4 resolution grids. It is important that the correct grid is drawn round, you should work from left to right with the 1.1mm grid being surrounded by the red box, 1.0mm by the green box, 0.9mm by the blue box and 0.8mm by the yellow box. In practice this simple means draw boxes from left to right on the image. If you wish to redraw a box, simply right click within it and redraw it. Please note, at the bottom of the image there is an option to zoom in which will help with accurate drawing. 

![image](https://github.com/user-attachments/assets/0a694a64-f1f8-4a5f-bd38-2ee15548d490)

## Tolerance Table
The tolerance table is used to quickly identify if a test is within tolerance. The tolerance table is in the ToleranceTable/ToleranceTable.xml file. In order to add a test to the tolerance table, you must add an XML element called module with the name field set to be the same as the module in question. For each module you can then add test tolerances, a child element is then added named Test. In each element the name field must be set to be equal to the specific test result (for example "1.1mm holes Horizontal").  You can then set a Min, Max or Equals value in this element. If the value is greater than min, lower than max or equal to the tolerance then it is considered within tolerance. If a module or test is not found in the tolerance table, then the script returns "No Tolerance Set". If no name is set on the test element, then the same tolerance is used for every test in that module.

## Testing Protocol 
To confirm the scripts, match expected results a testing protocol was developed. The goal of this was test each module and confirm it meets manual measurements is within a given tolerance. This testing protocol can be found [here](https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/MedACRTestingSetAndResults/Hazen%20Test%20Plan.docx) and the results found [here](https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/MedACRTestingSetAndResults/ACR%20Test%20Document%20%20V1.xlsx). Be sure to click Download Raw File to get the file without downloading the whole repo.

## Bug Reports and Feature Requests
Please make any bug reports or feature requests by logging an issue [here](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/issues) or send an email to the developers below. 

## Developers
John Tracey NHS Highland (John.tracey@nhs.scot)  <br />
Hamish Richardson NHS Lothian (hamish.richardson@nhs.scot)
