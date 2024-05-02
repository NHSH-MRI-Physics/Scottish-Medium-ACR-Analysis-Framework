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
### Requirements 
- [Docker](https://www.docker.com/products/docker-desktop/)
### Installation 
1. Download the [GUI Package](https://scottish-my.sharepoint.com/:u:/g/personal/john_tracey_nhsh_nhs_scot/EX5Y-Kya6olArn-rsOz0x4AB7nc_5kFH1e2-tw-V3Nl2yQ?e=x7VDTT) (click download at the top left). You will need a NHS Scotland email address to access this. In the future we will explore other hosting options.
2. unzip the folder somewhere convienant
3. Ensure Docker Desktop is [installed](https://docs.docker.com/desktop/install/windows-install/).
### Quick Start
1. Before each use ensure Docker Desktop is [running](https://docs.docker.com/desktop/install/windows-install/).
2. Run the ACR Phantom GUI file.
3. Refer to the image below for instructions on how to use the GUI.
![Quickstart Image](https://i.imgur.com/MqiAZBT.png)


## Python 
### Requirements 
- Python 3
### Installation
- Download this repository by clicking [here](https://github.com/NHSH-MRI-Physics/Hazen-ScottishACR-Fork/archive/refs/heads/main.zip).
- unzip and navigate to where you unzipped it.
- It is recommended a virtual environment is used to ensure no conflicts, see [here](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/) for instructions.
- enter `pip install -r requirements.txt` to install all dependencies. 
### Quick Start
- To run analysis use `python RunMedACRAnalysis.py -seq <Sequence Name> <Args>`
- Run `python .\RunMedACRAnalysis.py -h` to get a description of all arguments.
