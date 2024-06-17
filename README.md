![example workflow](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/actions/workflows/Run_UnitTests.yml/badge.svg)

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

## GUI 
### Requiremenets 
- None
### Installation
- Download the latest [release](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/releases/latest).
- Unzip the file and navigate to where it was downloaded.
- Double click and start ACR QA Analysis.exe.
- Select the location of the DICOM folder using the "Set DICOM Path" button.
- Select where the results will be outputted to usign the "Set Results Output Path" button.
- Select what sequence to analyse using the dropdown.
- Select whats tests you want to run from the checkboxes.
- Click "Start Analysis"
- On completion the results are displaeyd and you can view individual results by selecting the dropdown (below the "Start Analysis" button) following the "View Results" button.
## Python 
### Requirements 
- Python 3
### Installation
- Download this repository by clicking [here](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/archive/refs/heads/main.zip) or clone the repository.
- unzip and navigate to where you unzipped it.
- It is recommended a virtual environment is used to ensure no conflicts, see [here](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/) for instructions.
- enter `pip install -r requirements.txt` to install all dependencies. 
### Quick Start
- To run analysis use `python RunMedACRAnalysis.py -seq <Sequence Name> <Args>`
- Run `python .\RunMedACRAnalysis.py -h` to get a description of all arguments.
