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
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW
import MedACRAnalysis
import os 
import HighlightText
import glob 
import subprocess
import platform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
from MedACRAnalysis import *
import datetime
import numpy as np
import VariableHolder
import copy

try:
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
            
    root = tkinter.Tk()
    sv_ttk.set_theme("dark")
    root.geometry('1200x500')
    root.title('Medium ACR Phantom QA Analysis Pre-Release')
    root.iconbitmap("_internal\ct-scan.ico")

    VarHolder=VariableHolder.VarHolder()

    def SetDCMPath():
        dropdownResults.config(state="disabled")
        ViewResultsBtn.config(state="disabled")
        global InitalDirDICOM
        if InitalDirDICOM==None:
            filename = filedialog.askdirectory()
        else:
            filename = filedialog.askdirectory(initialdir=InitalDirDICOM)

        if filename=="":
            return
        DCMfolder_path.set(filename)
        InitalDirDICOM=DCMfolder_path.get()

        options=[]
        files = get_dicom_files(DCMfolder_path.get())
        sequences = []
        for file in files:
            data = pydicom.dcmread(file)
            if "Loc" not in data.SeriesDescription and "loc" not in data.SeriesDescription:
                options.append(data.SeriesDescription)

        options= list(set(options))
        options.sort()
        options.append(options[0])
        dropdown.set_menu(*options)
        dropdown.config(state="normal")


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
        else:
            for widgets in WidgetsToToggle:
                widgets.config(state="disabled")

    def ImageResolvable(newwindow):
        VarHolder.ROI_Results_ResResults[VarHolder.CurrentROI] = True
        newwindow.destroy()

    def ImageNotResolvable(newwindow):
        VarHolder.ROI_Results_ResResults[VarHolder.CurrentROI] = False
        newwindow.destroy()

    def ResetWindowing():
        BaseVmax = np.max(VarHolder.CurrentImage)
        BaseVmin = np.min(VarHolder.CurrentImage)
        VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
        VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0
        VarHolder.WinLevelLabel.config(text = "Window Level: " + str(VarHolder.CurrentLevel))
        VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(VarHolder.CurrentWidth))
        plot()

    def AdjustWindowWithKeyboard(event):
        key = event.keysym
        if key == "Left":
            VarHolder.CurrentWidth -=1
        elif key == "Right":
            VarHolder.CurrentWidth +=1
        elif key == "Up":
            VarHolder.CurrentLevel +=1
        elif key == "Down":
            VarHolder.CurrentLevel -=1
        
        if VarHolder.CurrentWidth <0:
            VarHolder.CurrentWidth=0

        VarHolder.WinLevelLabel.config(text = "Window Level: " + str(VarHolder.CurrentLevel))
        VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(VarHolder.CurrentWidth))

        Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
        Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth
        plot(Vmin=Vmin,Vmax=Vmax)


    def ManualRes(ROIS):
        for key in ROIS:
            VarHolder.ROI_Results_ResResults[key]=None
            VarHolder.CurrentROI=key
            print ("Displaying Res Pattern: " +key)
            VarHolder.newWindow =  tkinter.Toplevel(root)
            
            VarHolder.newWindow.iconbitmap("_internal\ct-scan.ico")
            VarHolder.newWindow.geometry("500x540")
            VarHolder.newWindow.configure(background='white')
            plt.title(key)
            VarHolder.CurrentImage = ROIS[key]
            BaseVmax = np.max(VarHolder.CurrentImage)
            BaseVmin = np.min(VarHolder.CurrentImage)
            VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
            VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0

            #plt.imshow(VarHolder.CurrentImage,cmap="gray",vmin=BaseVmin,vmax = BaseVmax)
            plot()
            VarHolder.Canvas = FigureCanvasTkAgg(plt.gcf(), master = VarHolder.newWindow)   
            VarHolder.Canvas.draw() 
            VarHolder.Canvas.get_tk_widget().pack(side=TOP)
            toolbar = NavigationToolbar2Tk(VarHolder.Canvas, VarHolder.newWindow) 
            toolbar.update() 
            VarHolder.Canvas.get_tk_widget().pack() 

            ResetWindowingBtn = ttk.Button(VarHolder.newWindow, text="Reset Windowing",width=20, command =ResetWindowing)
            ResetWindowingBtn.place(relx=0.4, rely=0.89, anchor="center")

            VarHolder.WinLevelLabel = ttk.Label(VarHolder.newWindow, text="Window Level: " + str(VarHolder.CurrentLevel), background="white", foreground="black")
            VarHolder.WinLevelLabel.place(relx=0.8, rely=0.86,anchor="center")
            VarHolder.WinWidthLabel = ttk.Label(VarHolder.newWindow, text="Window Width: "+ str(VarHolder.CurrentWidth), background="white", foreground="black")
            VarHolder.WinWidthLabel.place(relx=0.8, rely=0.90,anchor="center")

            VarHolder.newWindow.bind("<ButtonPress-1>", StartTracking)
            VarHolder.newWindow.bind("<ButtonRelease-1>", EndTracking)
            VarHolder.newWindow.bind("<B1-Motion>", Windowing_handler)

            VarHolder.newWindow.bind('<Key>', AdjustWindowWithKeyboard)

            root.wait_window(VarHolder.newWindow)
            plt.close()

    def Windowing_handler(event):
        if VarHolder.StartingEvent != None:
            Delta = datetime.datetime.now() - VarHolder.TimeOfLastEvent
            if (Delta.total_seconds() > 0.0001):

                #This isnt working as intended....
                #Issue is this bit is consntatly adding everytime its moving when it should only add when the moust button is released.
                WidthChange = event.x - VarHolder.StartingEvent.x
                LevelChange = VarHolder.StartingEvent.y - event.y
                
                VarHolder.CurrentLevel += (LevelChange)
                VarHolder.CurrentWidth += (WidthChange)
                if VarHolder.CurrentWidth <0:
                    VarHolder.CurrentWidth=0

                VarHolder.WinLevelLabel.config(text = "Window Level: " + str(VarHolder.CurrentLevel))
                VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(VarHolder.CurrentWidth))
                
                VarHolder.TimeOfLastEvent = datetime.datetime.now()
    
    def StartTracking(event):
        VarHolder.StartingEvent=copy.copy(event)

    def EndTracking(event):
        VarHolder.StartingEvent=None
        Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
        Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth
        plot(Vmin=Vmin,Vmax=Vmax)
        VarHolder.Canvas.draw()


    def plot(Vmin=None,Vmax=None):
        if Vmin != None and Vmax != None:
            plt.imshow(VarHolder.CurrentImage,cmap="gray",vmin=Vmin,vmax=Vmax)
        else:
            plt.imshow(VarHolder.CurrentImage,cmap="gray")
        #if VarHolder.Canvas!=None:
        #    VarHolder.Canvas.draw()

    def SetOptions():
        MedACRAnalysis.GeoMethod = GeometryOptions.ACRMETHOD
        if GeoAccOption.get() == "MagNet Method":
            MedACRAnalysis.GeoMethod=GeometryOptions.MAGNETMETHOD

        MedACRAnalysis.SpatialResMethod=ResOptions.DotMatrixMethod
        if SpatalResOption.get() == "MTF":
            MedACRAnalysis.SpatialResMethod=ResOptions.MTFMethod
        elif SpatalResOption.get() == "Contrast Response":
            MedACRAnalysis.SpatialResMethod=ResOptions.ContrastResponseMethod
        elif SpatalResOption.get() == "Manual":
            MedACRAnalysis.SpatialResMethod=ResOptions.Manual

    def RunAnalysis():
        RunAll=False
        SNR=False
        GeoAcc=False
        SpatialRes=False
        Uniformity=False
        Ghosting=False
        SlicePos=False
        SliceThickness=False

        if CheckBoxes["RunAll"][0].get()==1 and str(CheckBoxes["RunAll"][1]['state'])=="normal":
            RunAll=True
        else:
            if CheckBoxes["SNR"][0].get() == 1 and str(CheckBoxes["SNR"][1]['state'])=="normal":
                SNR=True
            if CheckBoxes["Geometric Accuracy"][0].get() == 1 and str(CheckBoxes["Geometric Accuracy"][1]['state'])=="normal":
                GeoAcc=True
            if CheckBoxes["Spatial Resolution"][0].get() == 1 and str(CheckBoxes["Spatial Resolution"][1]['state'])=="normal":
                SpatialRes=True
            if CheckBoxes["Uniformity"][0].get() == 1 and str(CheckBoxes["Uniformity"][1]['state'])=="normal":
                Uniformity=True
            if CheckBoxes["Ghosting"][0].get() == 1 and str(CheckBoxes["Ghosting"][1]['state'])=="normal":
                Ghosting=True
            if CheckBoxes["Slice Position"][0].get() == 1 and str(CheckBoxes["Slice Position"][1]['state'])=="normal":
                SlicePos=True
            if CheckBoxes["Slice Thickness"][0].get() == 1 and str(CheckBoxes["Slice Thickness"][1]['state'])=="normal":
                SliceThickness=True
        
        if DCMfolder_path.get()=="Not Set!":
            messagebox.showerror("Error", "No DICOM Path Set")
        if Resultsfolder_path.get()=="Not Set!":
            messagebox.showerror("Error", "No Results Path Set")
        EnableOrDisableEverything(False)

        SetOptions()
        MedACRAnalysis.ManualResTestText=None
        if SpatalResOption.get()=="Manual":
            ROIS = MedACRAnalysis.GetROIFigs(selected_option.get(),DCMfolder_path.get())
            plt.close('all')#Making sure no rogue plots are sitting in the background...
            ManualRes(ROIS)
            MedACRAnalysis.ManualResTestText = VarHolder.ROI_Results_ResResults
            #SpatialRes=False
        MedACRAnalysis.RunAnalysis(selected_option.get(),DCMfolder_path.get(),Resultsfolder_path.get(),RunAll=RunAll, RunSNR=SNR, RunGeoAcc=GeoAcc, RunSpatialRes=SpatialRes, RunUniformity=Uniformity, RunGhosting=Ghosting, RunSlicePos=SlicePos, RunSliceThickness=SliceThickness)
        EnableOrDisableEverything(True)

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
    DCMPathLabel.grid(row=0, column=1,padx=10,pady=2,columnspan=2,sticky=W)

    PathFrame = ttk.Frame(root)
    ResultsPathButton = ttk.Button(text="Set Results Output Path", command=SetResultsOutput,width=22)
    ResultsPathButton.grid(row=1, column=0,padx=10,pady=2,sticky=W)
    WidgetsToToggle.append(ResultsPathButton)
    Resultsfolder_path = StringVar()
    Resultsfolder_path.set("Not Set!")
    Resultsfolder_path.set("C:\\Users\John\Desktop\OutputTest") #Just cos im lazy and dont want to press the button tons when testing try and remember to remove it...
    ResultsPathLabel = ttk.Label(master=root,textvariable=Resultsfolder_path)
    ResultsPathLabel.grid(row=1, column=1,padx=10,pady=2,sticky=W,columnspan=2)

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
    frameResults.grid(row=2, column=1,padx=10,pady=10,rowspan=9,columnspan=3)

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
    sys.stderr = TextRedirector(TextLog, "stderr")
    frameLog.grid(row=11, column=1,padx=10,pady=10,rowspan=3,sticky=W,columnspan=2)

    Optionsframe = ttk.Frame(root)
    OptionsLabel = ttk.Label(master=Optionsframe,text="Options")
    OptionsLabel.pack(anchor=W)
    

    #ManualResCheck = IntVar(value=0)
    #ManualResBox = ttk.Checkbutton(Optionsframe, text='Use Manual Resolution Check',variable=ManualResCheck, onvalue=1, offvalue=0,state=NORMAL,command=None)
    #ManualResBox.pack(anchor=W)

    MiniFrame = ttk.Frame(Optionsframe)
    label = ttk.Label(MiniFrame, text="Spatial Res Method", anchor='w')
    options = ["Dot Matrix","Dot Matrix", "MTF", "Contrast Response", "Manual", ] 
    SpatalResOption = StringVar() 
    drop = ttk.OptionMenu( MiniFrame , SpatalResOption , *options ) 
    drop.config(width = 13)
    drop.grid(row=0, column=0,padx=5)
    label.grid(row=0, column=1)
    MiniFrame.pack(anchor=W)

    MiniFrame = ttk.Frame(Optionsframe)
    label = ttk.Label(MiniFrame, text="Geo Acc Method", anchor='w')
    options = [ "ACR Method", "ACR Method", "MagNet Method", ] 
    GeoAccOption = StringVar() 
    drop = ttk.OptionMenu( MiniFrame , GeoAccOption , *options ) 
    drop.config(width = 13)
    drop.grid(row=0, column=0,padx=5)
    label.grid(row=0, column=1)
    MiniFrame.pack(anchor=W)

    Optionsframe.grid(row=11, column=3,padx=10,pady=10,rowspan=3,sticky=NW)
    root.resizable(False,False)

    import hazenlib.logger

    hazenlib.logger.ConfigureLoggerForGUI()
    MedACR_ToleranceTableChecker.SetUpToleranceTable()

    root.mainloop()
except Exception as e:
    messagebox.showerror("Error", e) 