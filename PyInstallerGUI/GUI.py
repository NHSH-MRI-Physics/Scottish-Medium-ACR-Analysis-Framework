import shutil
import tkinter
from tkinter import ttk
import sv_ttk
from tkinter import filedialog
from tkinter import StringVar
from tkinter import IntVar
import sys
sys.path.append(".")
from hazenlib.utils import get_dicom_files
import pydicom
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW, CENTER
import MedACRAnalysisV2 as MedACRAnalysis
import os 
import HighlightText
import glob 
import subprocess
import platform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
from MedACRAnalysisV2 import *
import datetime
import numpy as np
import VariableHolder
from hazenlib._version import __version__
import threading
import webbrowser
import DICOM_Holder
import OptionsPane
import Windows
from threading import Thread

if getattr(sys, 'frozen', False):
    import pyi_splash

if getattr(sys, 'frozen', False):
    pyi_splash.close()

UseLegacyLoading = False #incase it doenst work this lets me quickly roll it back
Options_HolderDict = {}
try:
    #This is used with the plotly dash which has currently been shelved, 
    #proc = subprocess.Popen(['DataDashboard_Plotly\ACR_Data_Dashboard.exe'], stderr=sys.stderr, stdout=sys.stdout)

    class TextRedirector(object):
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, string):
            self.widget.configure(state="normal")
            self.widget.insert("end", string, (self.tag,))
            self.widget.configure(state="disabled")
            self.widget.see("end")
            root.update()

    class TextRedirectorErr(object):
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, string):
            self.widget.configure(state="normal")
            self.widget.insert("end", string, (self.tag,))
            self.widget.configure(state="disabled")
            self.widget.see("end")
            EnableOrDisableEverything(True) #I need to rethink this but it lets the program be used after a exception was thrown, might require a fair bit of reworking though...
            root.update()
            
    root = tkinter.Tk()
    #This need to be done after the root is called
    OptionsPaneObj = OptionsPane.OptionsPaneHolder()
    sv_ttk.set_theme("dark")
    root.geometry('1200x550')
    root.title('Medium ACR Phantom QA Analysis ' + __version__)
    root.iconbitmap("_internal\ct-scan.ico")

    def Tidyup():
        #This is to kill the datadash if we ever go back to it 
        #import psutil
        #PROCNAME = "ACR_Data_Dashboard.exe"
        #for proc in psutil.process_iter():
        #    if proc.name() == PROCNAME:
        #        proc.kill()

        sys.stdout = None
        sys.stderr = None
        if VarHolder.NewWindow!= None:
            VarHolder.NewWindow.destroy()
        if os.path.exists("TempDICOM"):
            shutil.rmtree("TempDICOM")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", Tidyup)

    VarHolder=VariableHolder.VarHolder()

    def SetDCMPath():
        global InitalDirDICOM
        if InitalDirDICOM==None:
            filename = filedialog.askdirectory()
        else:
            filename = filedialog.askdirectory(initialdir=InitalDirDICOM)

        if filename=="":
            return
        
        LoadDICOMDir(filename)

    def LoadPreviousRun():
        if InitalDirDICOM==None:
            PrevRun = filedialog.askopenfilename()
        else:
            PrevRun = filedialog.askopenfilename(initialdir=InitalDirDICOM)

        if PrevRun=="":
            return
        
        with open(PrevRun, 'rb') as f:
            data = pickle.load(f)

        if not os.path.exists("TempDICOM"):
            os.makedirs("TempDICOM")
        VarHolder.PreviousLoadedDataDump = data
        DICOMData = data["DICOM"]
        DICOMS = []
        count = 1
        for DICOM in data["DICOM"]:
            DICOM.save_as(os.path.join("TempDICOM",str(count)+".dcm"))
            DICOMS.append(os.path.join("TempDICOM",str(count)+".dcm"))
            count+=1
        
        #Prior to version 1.1 the dump file will only load the dicom, not the settings but it doens't really matter since their was no option for the user to do it anyway
        if "SettingsPaneOptions" in data:
            OptionsPaneObj.SetOptions(data["SettingsPaneOptions"])
        OptionsPaneObj.LoadPreviousRun.set(1) #Need this since this the only setting taht differs from that in the dump file
        LoadDICOMDir("TempDICOM")

        
        
        
    def LoadDICOMDir(filename):
        global InitalDirDICOM
        dropdownResults.config(state="disabled")
        ViewResultsBtn.config(state="disabled")

        DCMfolder_path.set(filename)
        InitalDirDICOM=DCMfolder_path.get()

        Seqs={}
        files = get_dicom_files(DCMfolder_path.get())
        sequences = []
        WarningMessages = []
        DICOM_Holder_Objs = []

        for file in files:
            data = pydicom.dcmread(file)
            if "Loc" not in data.SeriesDescription and "loc" not in data.SeriesDescription:
                if UseLegacyLoading == True:
                    #options.append(data.SeriesDescription)
                    #print( data.SeriesInstanceUID)
                    if data.SeriesDescription not in Seqs:
                        Seqs[data.SeriesDescription]=1
                    else:
                        Seqs[data.SeriesDescription]+=1
                else:
                    #new way of doing it which is better..
                    if len(DICOM_Holder_Objs)==0: #Stick the first DICOM in the list so we can start checking
                        DICOM_Holder_Objs.append(DICOM_Holder.DICOMSet(data,file))
                    else:
                        GotAtLeastOneMatch = False
                        for OneHolder in DICOM_Holder_Objs:
                            if OneHolder.Does_DICOM_Match(data) == True:
                                OneHolder.AddDICOM(data,file)
                                GotAtLeastOneMatch = True
                        if GotAtLeastOneMatch == False:
                            DICOM_Holder_Objs.append(DICOM_Holder.DICOMSet(data,file))
            else:
                WarningMessages.append("Series Description: " + data.SeriesDescription + " is assumed to be the localiser and not included")

        options=[]
        if UseLegacyLoading == True:
            for seq in Seqs.keys():
                if Seqs[seq] == 11:
                    options.append(seq)
                else:
                    WarningMessages.append("Series Description: " + seq + " has more than 11 slices and not included")
        else:
            #new way of doing it...
            KeptDICOMHolders = []
            for holder in DICOM_Holder_Objs:
                if len(holder.DICOM_Data) == 11:
                    options.append(holder.params["SeriesDescription"])
                    KeptDICOMHolders.append(holder)
                else:
                    WarningMessages.append("Series Description: " + holder.params["SeriesDescription"] + " has more than 11 slices and not included")

            Options_HolderDict = {}
            #options= list(set(options))
            duplicates = set([x for x in options if options.count(x) > 1])
            for dupe in duplicates: 
                DupeHolders = []
                DupeParamHolders = []
                for holder in KeptDICOMHolders:
                    if holder.params["SeriesDescription"] == dupe:
                        DupeHolders.append(holder)
                        DupeParamHolders.append(holder.params)
                keys = DupeParamHolders[0].keys()
                diffs = {}
                for key in keys:
                    values = []
                    for d in DupeParamHolders:
                        values.append(d[key])
                    if len(set(values)) > 1:
                        diffs[key] = values
                for i in range(len(DupeHolders)):
                    Prefix = ""
                    for key in diffs:
                        if key != "SeriesInstanceUID":
                            Prefix += key + ": " + str(diffs[key][i]) + ", "
                        else: 
                            if len(diffs.keys()) == 1:  # If the only key is SeriesInstanceUID, then use it otherwise dont
                                Prefix += key + ": " + str(diffs[key][i]) + ", "
                    Prefix = Prefix[:-2]  # Remove the last comma and space
                    name = DupeHolders[i].params["SeriesDescription"] + " " +Prefix
                    Options_HolderDict[name] = DupeHolders[i]

            for holder in KeptDICOMHolders:
                if holder.params["SeriesDescription"] not in duplicates:            
                    Options_HolderDict[holder.params["SeriesDescription"]] = holder
            options = list(Options_HolderDict.keys())
            MedACRAnalysis.DICOM_Holder_Dict = Options_HolderDict  

        options.sort()
        options.append(options[0])
        dropdown.set_menu(*options)
        dropdown.config(state="normal")

        WarningMessages = set(WarningMessages)
        if len(WarningMessages) > 0:
            for warn in WarningMessages:
                print(warn)



    def SetResultsOutput():
        global InitalDirOutput
        if InitalDirOutput==None:
            filename = filedialog.askdirectory()
        else:
            filename = filedialog.askdirectory(initialdir=InitalDirOutput)
        if filename=="":
            return
        Resultsfolder_path.set(filename)
        InitalDirOutput=Resultsfolder_path.get()

    def AdjustCheckBoxes():
        if CheckBoxes["RunAll"][0].get() == 0:
            for keys in CheckBoxes:
                if keys != "RunAll":
                    CheckBoxes[keys][1].config(state=NORMAL)
        
        if CheckBoxes["RunAll"][0].get() == 1:
            for keys in CheckBoxes:
                if keys != "RunAll":
                    CheckBoxes[keys][1].config(state=DISABLED)

    def EnableOrDisableEverything(Enable):
        if Enable==True:
            for widgets in WidgetsToToggle:
                widgets.config(state="normal")
                AdjustCheckBoxes()
        else:
            for widgets in WidgetsToToggle:
                widgets.config(state="disabled")
                
    def SetOptions():
        MedACRAnalysis.GeoMethod = GeometryOptions.ACRMETHOD
        if OptionsPaneObj.GetOptions()["GeoAccOption"] == "MagNet Method":
            MedACRAnalysis.GeoMethod=GeometryOptions.MAGNETMETHOD

        MedACRAnalysis.SpatialResMethod=ResOptions.DotMatrixMethod
        if OptionsPaneObj.GetOptions()["SpatialResOption"] == "MTF":
            MedACRAnalysis.SpatialResMethod=ResOptions.MTFMethod
        elif OptionsPaneObj.GetOptions()["SpatialResOption"] == "Contrast Response":
            MedACRAnalysis.SpatialResMethod=ResOptions.ContrastResponseMethod
        elif OptionsPaneObj.GetOptions()["SpatialResOption"] == "Manual":
            MedACRAnalysis.SpatialResMethod=ResOptions.Manual

        MedACRAnalysis.UniformityMethod = UniformityOptions.ACRMETHOD
        if OptionsPaneObj.GetOptions()["UniformityOptions"] == "MagNet Method":
            MedACRAnalysis.UniformityMethod = UniformityOptions.MAGNETMETHOD

        if OptionsPaneObj.GetOptions()["UseLegacySliceThicknessAlgo"] == 1:
            MedACRAnalysis.UseLegacySliceThicknessAlgo = True
        else:
            MedACRAnalysis.UseLegacySliceThicknessAlgo = False

        if OptionsPaneObj.GetOptions()["DumpToExcel"] == 1:
            MedACRAnalysis.DumpToExcel = True
        else:
            MedACRAnalysis.DumpToExcel = False

        MedACRAnalysis.SettingsPaneObject = OptionsPaneObj

    def RunAnalysis():
        if DCMfolder_path.get()=="Not Set!":
            messagebox.showerror("Error", "No DICOM Path Set")
            return
        if Resultsfolder_path.get()=="Not Set!":
            messagebox.showerror("Error", "No Results Path Set")
            return
        
        if DCMfolder_path.get() == Resultsfolder_path.get():
            messagebox.showerror("Error","Dicom and results folder cannot be the same")
            return

        RunAll=False
        SNR=False
        GeoAcc=False
        SpatialRes=False
        Uniformity=False
        Ghosting=False
        SlicePos=False
        SliceThickness=False

        AtLeatOneModuleSelected = False

        if CheckBoxes["RunAll"][0].get()==1 and str(CheckBoxes["RunAll"][1]['state'])=="normal":
            RunAll=True
            AtLeatOneModuleSelected = True
        else:
            if CheckBoxes["SNR"][0].get() == 1 and str(CheckBoxes["SNR"][1]['state'])=="normal":
                SNR=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Geometric Accuracy"][0].get() == 1 and str(CheckBoxes["Geometric Accuracy"][1]['state'])=="normal":
                GeoAcc=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Spatial Resolution"][0].get() == 1 and str(CheckBoxes["Spatial Resolution"][1]['state'])=="normal":
                SpatialRes=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Uniformity"][0].get() == 1 and str(CheckBoxes["Uniformity"][1]['state'])=="normal":
                Uniformity=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Ghosting"][0].get() == 1 and str(CheckBoxes["Ghosting"][1]['state'])=="normal":
                Ghosting=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Slice Position"][0].get() == 1 and str(CheckBoxes["Slice Position"][1]['state'])=="normal":
                SlicePos=True
                AtLeatOneModuleSelected = True
            if CheckBoxes["Slice Thickness"][0].get() == 1 and str(CheckBoxes["Slice Thickness"][1]['state'])=="normal":
                SliceThickness=True
                AtLeatOneModuleSelected = True

        if AtLeatOneModuleSelected == False:
            messagebox.showerror("Error", "No Modules Selected")
            return

        EnableOrDisableEverything(False)

        SetOptions()
        SlicesToOverride = []
        SlicesToOverride.append(7) # Every test uses slice 7
        if RunAll == True or GeoAcc == True:
            if OptionsPaneObj.GetOptions()["OverrideMasking"] == 1:
                if MedACRAnalysis.GeoMethod == GeometryOptions.ACRMETHOD:
                    SlicesToOverride.append(1)
                    SlicesToOverride.append(5)

        if OptionsPaneObj.GetOptions()["OverrideRadiusAndCentre"] == 1:
            SlicesToOverride.append(7)
        SlicesToOverride = sorted(set(SlicesToOverride))

        #Make sure slice 7 is always done first so we can get the radius/centre
        if 7 in SlicesToOverride:
            SlicesToOverride.remove(7)
            SlicesToOverride.insert(0,7)

        MedACRAnalysis.ParamaterOverides = ParamaterOveride()
        if VarHolder.LoadPreviousRunMode == True:
            #MedACRAnalysis.ParamaterOverides = VarHolder.PreviousLoadedDataDump["ParamaterOverides"]
            if OptionsPaneObj.GetOptions()["OverrideRadiusAndCentre"] == 1:
                MedACRAnalysis.ParamaterOverides.CentreOverride = VarHolder.PreviousLoadedDataDump["ParamaterOverides"].CentreOverride
                MedACRAnalysis.ParamaterOverides.RadiusOverride = VarHolder.PreviousLoadedDataDump["ParamaterOverides"].RadiusOverride
                OptionsPaneObj.OverrideRadiusAndCentre.set(0) #Turn it off that way we only show the dialog to reset if it the user wants to.
                Answer = messagebox.askyesno("Previous loaded override data present", "Do you wish to keep the previously loaded center override data?", icon='question')
                if Answer == False:
                    MedACRAnalysis.ParamaterOverides.CentreOverride = None
                    MedACRAnalysis.ParamaterOverides.RadiusOverride = None
                    OptionsPaneObj.OverrideRadiusAndCentre.set(1)

            if OptionsPaneObj.GetOptions()["OverrideMasking"] == 1:
                MedACRAnalysis.ParamaterOverides.MaskingOverride = VarHolder.PreviousLoadedDataDump["ParamaterOverides"].MaskingOverride
                OptionsPaneObj.OverrideMasking.set(0)
                Answer = messagebox.askyesno("Previous loaded override data present", "Do you wish to keep the previously loaded masking override data?", icon='question')
                if Answer == False:
                    TempParam = ParamaterOveride() #This is cause the masking override is a list so we need to copy it over properly
                    MedACRAnalysis.ParamaterOverides.MaskingOverride = TempParam.MaskingOverride
                    OptionsPaneObj.OverrideMasking.set(1)
            
            if OptionsPaneObj.GetOptions()["OverideResBlockLoc"] == 1:
                MedACRAnalysis.ParamaterOverides.ROIOverride = VarHolder.PreviousLoadedDataDump["ParamaterOverides"].ROIOverride
                OptionsPaneObj.OverideResBlockLoc.set(0)
                Answer = messagebox.askyesno("Previous loaded override data present", "Do you wish to keep the previously loaded res block ROI Location override data?", icon='question')
                if Answer == False:
                    MedACRAnalysis.ParamaterOverides.ROIOverride = None
                    OptionsPaneObj.OverideResBlockLoc.set(1)

        for CurrentSlice in SlicesToOverride:
            OverrideCurrentSlice = False
            if OptionsPaneObj.GetOptions()["OverrideRadiusAndCentre"] == 1 and CurrentSlice==7:
                OverrideCurrentSlice = True

            if OptionsPaneObj.GetOptions()["OverrideMasking"] == 1:
                OverrideCurrentSlice = True
            
            #if OptionsPane.GetOptions()["OverrideRadiusAndCentre"] == 1 or OptionsPane.GetOptions()["OverrideMasking"] == 1:
            if OverrideCurrentSlice == True: 
                OverrideCentreRadiusObj = Windows.CentreRadiusMaskingWindow(root,DCMfolder_path.get(),selected_option.get(),overridemasking=OptionsPaneObj.GetOptions()["OverrideMasking"],slice=CurrentSlice,PreCalcdCentre=MedACRAnalysis.ParamaterOverides.CentreOverride)
                OverrideCentreRadiusObj.GetCentreRadiusMask()

            if OptionsPaneObj.GetOptions()["OverrideRadiusAndCentre"] == 1 and CurrentSlice==7:
                print("Radius and Centre of phantom overriden")
                MedACRAnalysis.ParamaterOverides.CentreOverride = [OverrideCentreRadiusObj.Centrex,OverrideCentreRadiusObj.Centrey]
                MedACRAnalysis.ParamaterOverides.RadiusOverride = OverrideCentreRadiusObj.Radius

            if OptionsPaneObj.GetOptions()["OverrideMasking"] == 1:
                print("Mask of phantom overriden")
                MedACRAnalysis.ParamaterOverides.MaskingOverride[CurrentSlice-1] = OverrideCentreRadiusObj.Mask

        if (OptionsPaneObj.GetOptions()["OverideResBlockLoc"] == 1 and SpatialRes == True) or (OptionsPaneObj.GetOptions()["OverideResBlockLoc"] == 1 and RunAll==True):
            if MedACRAnalysis.SpatialResMethod != ResOptions.MTFMethod:
                overrideRes = Windows.GetROIOfResBlock(root,DCMfolder_path.get(),selected_option.get())
                if OptionsPaneObj.GetOptions()["FixedManualROISize"] == 0:
                    overrideRes.FixedSize = False
                overrideRes.GetROIs()
                MedACRAnalysis.ParamaterOverides.ROIOverride=overrideRes.crops

        if VarHolder.LoadPreviousRunMode == True:
            #This here reutrns the options back to the previous loaded ones since we only turned them off to show the dialog boxes
            OptionsPaneObj.OverrideRadiusAndCentre.set(VarHolder.PreviousLoadedDataDump["SettingsPaneOptions"]["OverrideRadiusAndCentre"])
            OptionsPaneObj.OverrideMasking.set(VarHolder.PreviousLoadedDataDump["SettingsPaneOptions"]["OverrideMasking"])
            OptionsPaneObj.OverideResBlockLoc.set(VarHolder.PreviousLoadedDataDump["SettingsPaneOptions"]["OverideResBlockLoc"])

        #ArrayToSave = []
        #ArrayToSave.append(MedACRAnalysis.ParamaterOverides.CentreOverride)
        #ArrayToSave.append(MedACRAnalysis.ParamaterOverides.RadiusOverride)
        #ArrayToSave.append(MedACRAnalysis.ParamaterOverides.MaskingOverride)
        #ArrayToSave.append(MedACRAnalysis.ParamaterOverides.ROIOverride)
        #np.savez("Override",ArrayToSave[0],ArrayToSave[1],ArrayToSave[2],ArrayToSave[3][0],ArrayToSave[3][1],ArrayToSave[3][2],ArrayToSave[3][3],allow_pickle=True)


        MedACRAnalysis.ManualResTestText=None
        MedACRAnalysis.ManualResData = None
        if OptionsPaneObj.GetOptions()["SpatialResOption"]=="Manual" and SpatialRes==True or RunAll==True and OptionsPaneObj.GetOptions()["SpatialResOption"]=="Manual":
            ROIS = MedACRAnalysis.GetROIFigs(selected_option.get(),DCMfolder_path.get())


            #DEBUGGING STUFF
            #del ROIS[list(ROIS.keys())[0]]
            #del ROIS[list(ROIS.keys())[0]]
            #del ROIS[list(ROIS.keys())[0]]

            plt.close('all')#Making sure no rogue plots are sitting in the background...
            #ManualRes(ROIS)
            ManualResObj = Windows.ManualResWindow(root)
            #MedACRAnalysis.ManualResData = VarHolder.ManualResData
            MedACRAnalysis.ManualResData = ManualResObj.ManualRes(ROIS)

            #SpatialRes=False

        textResults.configure(state="normal")
        MedACRAnalysis.ReportText = ''
        textResults.delete(1.0, END)
        textResults.configure(state="disabled")

        if UseLegacyLoading == True:
            MedACRAnalysis.RunAnalysis(selected_option.get(),DCMfolder_path.get(),Resultsfolder_path.get(),RunAll=RunAll, RunSNR=SNR, RunGeoAcc=GeoAcc, RunSpatialRes=SpatialRes, RunUniformity=Uniformity, RunGhosting=Ghosting, RunSlicePos=SlicePos, RunSliceThickness=SliceThickness)
        else:
            MedACRAnalysis.RunAnalysisWithHolder(selected_option.get(),DCMfolder_path.get(),Resultsfolder_path.get(),RunAll=RunAll, RunSNR=SNR, RunGeoAcc=GeoAcc, RunSpatialRes=SpatialRes, RunUniformity=Uniformity, RunGhosting=Ghosting, RunSlicePos=SlicePos, RunSliceThickness=SliceThickness)


        EnableOrDisableEverything(True)
        if RunAll==True:
            for keys in CheckBoxes:
                CheckBoxes[keys][1].config(state="disabled")
            CheckBoxes["RunAll"][1].config(state="normal")

        textResults.configure(state="normal")
        textResults.delete(1.0, END)
        textResults.insert("end", MedACRAnalysis.ReportText)
        textResults.tag_config("Pass", foreground="green")
        textResults.tag_config("Fail", foreground="red")
        textResults.tag_config("No Tolerance Set", foreground="yellow")
        textResults.highlight_pattern(r"Pass","Pass")
        textResults.highlight_pattern(r"Fail","Fail")
        textResults.highlight_pattern(r"No Tolerance Set","No Tolerance Set")
        textResults.configure(state="disabled")

        #Find all folders
        Folders = [x[0] for x in os.walk(Resultsfolder_path.get())]
        Indexofroot = Folders.index(Resultsfolder_path.get())
        del Folders[Indexofroot]
        DropDownOptions = []
        for folder in Folders:
            DropDownOptions.append(folder.split(os.sep)[-1])
        
        DropDownOptions.sort()
        DropDownOptions.append(DropDownOptions[0])
        dropdownResults.set_menu(*DropDownOptions)
        dropdownResults.config(state="normal")
        print ("Done")

    def ViewResult():
        ChosenResult = Result_Selection.get()
        Path = Resultsfolder_path.get()
        ChosenFolder = os.path.join(ChosenResult, Path)
        Files = glob.glob(os.path.join(ChosenFolder,ChosenResult,"*.png"))
        UnderScrolledSeq = selected_option.get().replace(' ','_')

        FilesToOpen = []
        for file in Files:
            if UnderScrolledSeq in file:
                if platform.system() == "Windows":
                    os.startfile(file)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, file])

    WidgetsToToggle=[]
    InitalDirDICOM=None
    InitalDirOutput=None

    PathFrame = ttk.Frame(root)
    DCMPathButton = ttk.Button(text="Set DICOM Path", command=SetDCMPath,width=22)
    DCMPathButton.grid(row=0, column=0,padx=10,pady=2,sticky=W)
    WidgetsToToggle.append(DCMPathButton)
    DCMfolder_path = StringVar()
    DCMfolder_path.set("Not Set!")
    DCMPathLabel = ttk.Label(master=root,textvariable=DCMfolder_path)
    DCMPathLabel.grid(row=0, column=1,padx=10,pady=2,columnspan=6,sticky=W)

    PathFrame = ttk.Frame(root)
    ResultsPathButton = ttk.Button(text="Set Results Output Path", command=SetResultsOutput,width=22)
    ResultsPathButton.grid(row=1, column=0,padx=10,pady=2,sticky=W)
    WidgetsToToggle.append(ResultsPathButton)
    Resultsfolder_path = StringVar()
    Resultsfolder_path.set("Not Set!")
    ResultsPathLabel = ttk.Label(master=root,textvariable=Resultsfolder_path)
    ResultsPathLabel.grid(row=1, column=1,padx=10,pady=2,sticky=W,columnspan=6)

    #Resultsfolder_path.set("C:\\Users\Johnt\Desktop\Out") #Just cos im lazy and dont want to press the button tons when testing try and remember to remove it...

    selected_option = StringVar(root)
    options = [] 
    dropdown = ttk.OptionMenu(root, selected_option, *options)
    dropdown.config(width = 20,state="disabled")
    WidgetsToToggle.append(dropdown)
    dropdown.grid(row=2, column=0,padx=10,pady=10)

    CheckBoxes = {}
    CheckBoxes["RunAll"] = [None,None]
    CheckBoxes["Uniformity"] = [None,None]
    CheckBoxes["Slice Position"] = [None,None]
    CheckBoxes["Spatial Resolution"] = [None,None]
    CheckBoxes["Slice Thickness"] = [None,None]
    CheckBoxes["SNR"] = [None,None]
    CheckBoxes["Geometric Accuracy"] = [None,None]
    CheckBoxes["Ghosting"] = [None,None]
    StartingRow = 4
    for keys in CheckBoxes:
        if keys == "RunAll":
            CheckBoxes["RunAll"][0] = IntVar(value=1)
            CheckBoxes["RunAll"][1] = ttk.Checkbutton(root, text='Run All',variable=CheckBoxes["RunAll"][0], onvalue=1, offvalue=0,state=NORMAL,command=AdjustCheckBoxes)
            CheckBoxes["RunAll"][1].grid(row=3, column=0,sticky=W)
            WidgetsToToggle.append(CheckBoxes["RunAll"][1])
        else:
            CheckBoxes[keys][0] = IntVar(value=0)
            CheckBoxes[keys][1] = ttk.Checkbutton(root, text="Run "+keys,variable=CheckBoxes[keys][0], onvalue=1, offvalue=0,state=DISABLED,command=AdjustCheckBoxes)
            CheckBoxes[keys][1].grid(row=StartingRow, column=0,sticky=W)
            StartingRow+=1
            WidgetsToToggle.append(CheckBoxes[keys][1])

    RunAnalysisBtn = ttk.Button(text="Start Analysis",width=22,command=RunAnalysis)
    RunAnalysisBtn.grid(row=StartingRow, column=0,padx=10,pady=10,sticky=W)
    WidgetsToToggle.append(RunAnalysisBtn)

    ViewResultsBtn = ttk.Button(text="View Results",width=22,command=ViewResult,state=DISABLED)
    ViewResultsBtn.grid(row=StartingRow+2, column=0,padx=10,pady=0,sticky=W)
    WidgetsToToggle.append(ViewResultsBtn)

    Result_Selection = StringVar()
    ResultImages = [] 
    dropdownResults = ttk.OptionMenu(root, Result_Selection, *ResultImages)
    dropdownResults.config(width = 20,state="disabled")
    WidgetsToToggle.append(dropdownResults)
    dropdownResults.grid(row=StartingRow+1, column=0,padx=10,pady=0,sticky=W)

    frameResults = ttk.Frame(root)
    ResultsWindowLabel = ttk.Label(master=frameResults,text="Results")
    ResultsWindowLabel.pack(anchor=W)

    scroll = ttk.Scrollbar(frameResults) 
    scroll.pack(side="right",fill="y")
    textResults = HighlightText.CustomText(frameResults, height=15, width=118,state=DISABLED,yscrollcommand = scroll.set) 
    scroll.config(command=textResults.yview)
    textResults.configure(yscrollcommand=scroll.set) 
    textResults.pack()
    frameResults.grid(row=2, column=1,padx=10,pady=0,rowspan=9,columnspan=3)

    frameLog = ttk.Frame(root)
    LogWindowLabel = ttk.Label(master=frameLog,text="Log")
    LogWindowLabel.pack(anchor=W)
    scrollLog = ttk.Scrollbar(frameLog) 
    scrollLog.pack(side="right",fill="y")
    TextLog = tkinter.Text(frameLog, height=7, width=80,state=DISABLED,yscrollcommand = scroll.set) 
    scrollLog.config(command=textResults.yview)
    TextLog.configure(yscrollcommand=scrollLog.set) 
    TextLog.pack(anchor=W)

    sys.stdout = TextRedirector(TextLog, "stdout")
    sys.stderr = TextRedirectorErr(TextLog, "stderr")
    frameLog.grid(row=11, column=1,padx=10,pady=10,rowspan=3,sticky=W,columnspan=2)

    Optionsframe = ttk.Frame(root)
    #OptionsLabel = ttk.Label(master=Optionsframe,text="Options")
    #OptionsLabel.pack(anchor=W)


    def CloseOptionsPane(Window):
        Window.destroy()

    def OpenOptionsPane():
        OptionsPaneWin = tkinter.Toplevel(root)
        OptionsPaneWin.grab_set()
        OptionsPaneWin.iconbitmap("_internal\ct-scan.ico")
        OptionsPaneWin.geometry("800x540")
        OptionsPaneWin.resizable(False,False)
        def disable_event():
            pass
        OptionsPaneWin.protocol("WM_DELETE_WINDOW", disable_event)

        label = ttk.Label(OptionsPaneWin, text="Options Menu")
        label.place(relx=0.5, rely=0.02, anchor=CENTER)

        SelectionFrame = ttk.Frame(OptionsPaneWin)
        SelectionFrame.pack(side="top", fill="x", expand=False,pady=50)

        closeBtn = ttk.Button(OptionsPaneWin, text="Close Options",width=20,command = lambda: CloseOptionsPane(OptionsPaneWin))
        closeBtn.place(relx=0.5, rely=0.96, anchor=CENTER)

        OptionsPaneObj.SetupOptions(SelectionFrame)
        #OptionsPane.GetOptions()

        root.wait_window(OptionsPaneWin)

        if OptionsPaneObj.GetOptions()["LoadPreviousRun"] == 1:
            DCMPathButton.config(text="Load in previous run",command=LoadPreviousRun)
            VarHolder.LoadPreviousRunMode = True
        else:
            DCMPathButton.config(text="Set DICOM Path", command=SetDCMPath)
            DCMPathButton.config(text="Set DICOM Path")
            VarHolder.LoadPreviousRunMode = False
        

    def OpenManual():
        webbrowser.open('https://github.com/NHSH-MRI-Physics/Scottish-Medium-ACR-Analysis-Framework/blob/main/README.md', new=0)

    def OpenBugFeatureSite():
        webbrowser.open('https://forms.cloud.microsoft/e/9ZsZNbTinT?origin=QRCode', new=0)

    def OpenDatabaseForm():
        webbrowser.open('https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=veDvEDCgykuAnLXmdF5JmpoBwhWxYCZJmZebFt_oEWNUNk9TVThLRTYwWDlJSVM5VkI5WlJBQTA0OC4u&origin=QRCode', new=0)

    def ViewDICOMS():
        if DCMfolder_path.get() == "Not Set!":
            messagebox.showerror("Error", "Set DICOM Path first!")
            return
        ViewDICOMObj = Windows.DisplayLoadedDICOM(root,DCMfolder_path.get(),selected_option.get())
        ViewDICOMObj.DiplayDICOMS()

    OpenOptionsButton = ttk.Button(Optionsframe, text="Open Options",width=20,command = OpenOptionsPane)
    OpenOptionsButton.pack(pady=1)

    ManualButton = ttk.Button(Optionsframe, text="Open Manual",width=20,command = OpenManual)
    ManualButton.pack(pady=1)

    BugReporting = ttk.Button(Optionsframe, text="Bug reporting and \n feature requesting",width=20,command = OpenBugFeatureSite)
    BugReporting.pack(pady=1)

    ReportData = ttk.Button(Optionsframe, text="Report Data",width=20,command = OpenDatabaseForm)
    ReportData.pack(pady=1)

    BugReporting = ttk.Button(Optionsframe, text="View Loaded DICOM",width=20,command = ViewDICOMS)
    BugReporting.pack(pady=1)

    Optionsframe.grid(row=11, column=3,padx=8,pady=5,rowspan=3)
    root.resizable(False,False)

    import hazenlib.logger

    hazenlib.logger.ConfigureLoggerForGUI()
    MedACR_ToleranceTableChecker.SetUpToleranceTable()


    root.mainloop()
except Exception as e:
    messagebox.showerror("Error", e) 