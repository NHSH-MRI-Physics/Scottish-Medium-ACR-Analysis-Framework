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
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END
import MedACRAnalysis
import os 
#import HighlightText

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
root.geometry('1200x500')


def SetDCMPath():
    filename = filedialog.askdirectory()
    if filename=="":
        return
    DCMfolder_path.set(filename)

    options=[]
    files = get_dicom_files("MedACRTesting/TestData/ACR_Phantom_Data")
    sequences = []
    for file in files:
        data = pydicom.dcmread(file)
        if "Loc" not in data.SeriesDescription and "loc" not in data.SeriesDescription:
            options.append(data.SeriesDescription)

    options= list(set(options))
    option=options.sort()
    dropdown.set_menu(*options)
    dropdown.config(state="normal")


def SetResultsOutput():
    filename = filedialog.askdirectory()
    if filename=="":
        return
    Resultsfolder_path.set(filename)

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
    MedACRAnalysis.RunAnalysis(selected_option.get(),DCMfolder_path.get(),Resultsfolder_path.get(),RunAll=RunAll, RunSNR=SNR, RunGeoAcc=GeoAcc, RunSpatialRes=SpatialRes, RunUniformity=Uniformity, RunGhosting=Ghosting, RunSlicePos=SlicePos, RunSliceThickness=SliceThickness)
    EnableOrDisableEverything(True)

    textResults.configure(state="normal")
    textResults.delete(1.0, END)
    textResults.insert("end", MedACRAnalysis.ReportText)
    textResults.configure(state="disabled")

    print ("Done")



WidgetsToToggle=[]

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
#Resultsfolder_path.set("C:\\Users\John\Desktop\OutputTest") #Just cos im lazy and dont want to press the button tons when testing try and remember to remove it...
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

ViewResultsBtn = ttk.Button(text="View Results",width=22,command=None,state=DISABLED)
ViewResultsBtn.grid(row=StartingRow+2, column=0,padx=10,pady=0,sticky=W)
WidgetsToToggle.append(ViewResultsBtn)

Result_Selection = StringVar()
ResultImages = [] 
dropdownResults = ttk.OptionMenu(root, Result_Selection, *ResultImages)
dropdownResults.config(width = 20,state="disabled")
WidgetsToToggle.append(dropdownResults)
dropdownResults.grid(row=StartingRow+1, column=0,padx=10,pady=0,sticky=W)



frame = ttk.Frame(root)
ResultsWindowLabel = ttk.Label(master=frame,text="Results")
ResultsWindowLabel.pack(anchor=W)

scroll = ttk.Scrollbar(frame) 
scroll.pack(side="right",fill="y")
textResults = tkinter.Text(frame, height=15, width=118,state=DISABLED,yscrollcommand = scroll.set) 
scroll.config(command=textResults.yview)
textResults.configure(yscrollcommand=scroll.set) 
textResults.pack()
frame.grid(row=2, column=2,padx=10,pady=10,rowspan=9)

frame = ttk.Frame(root)
LogWindowLabel = ttk.Label(master=frame,text="Log")
LogWindowLabel.pack(anchor=W)
scrollLog = ttk.Scrollbar(frame) 
scrollLog.pack(side="right",fill="y")
TextLog = tkinter.Text(frame, height=7, width=118,state=DISABLED,yscrollcommand = scroll.set) 
scrollLog.config(command=textResults.yview)
TextLog.configure(yscrollcommand=scrollLog.set) 
TextLog.pack()

sys.stdout = TextRedirector(TextLog, "stdout")
sys.stderr = TextRedirector(TextLog, "stderr")
frame.grid(row=11, column=2,padx=10,pady=10,rowspan=3)

sv_ttk.set_theme("dark")
root.resizable(False,False)
root.mainloop()