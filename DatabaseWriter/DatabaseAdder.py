import tkinter as tk
from tkinter import N, NE, NW, W, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import StringVar, Radiobutton, TOP
import StandardConfirmation
from tkinter import messagebox
import pickle
import sys
import os
sys.path.append(".")
import os
import gspread
from MedACROptions import *
import MedACRModules
from MedACRModules.Empty_Module import EmptyModule
from tkinter import simpledialog


sys.path.append("PyInstallerGUI")

root = TkinterDnD.Tk()
root.title("Database Checker and Adder")
root.geometry("800x450")  # Width x Height
resultDict = None
Weighting = StringVar(root, "T1") 
Coil = StringVar(root, "Head") 
Orientation = StringVar(root, "Axial") 
data = None

# Label placed at the top-left corner
label = tk.Label(
    root,
    text="Drag and drop a file here",
    width=40,
    height=5,
    bg="lightgray",
    anchor="center",        # Align text to the left inside the label
    justify="center",    # Align multiline text to the left
    font=("Arial", 12),
)
label.grid(padx=10, pady=10,row=0, column=0)

StandardLabel = tk.Label(
    root,
    text="No File Dropped",  
    width=40,
    height=5,
    bg="lightgray",
    anchor="center",        # Align text to the left inside the label
    justify="center",    # Align multiline text to the left
    font=("Arial", 12)
)
StandardLabel.grid(padx=10, pady=10,row=0, column=1)

FileDropped = tk.Label(
    root,
    text="No File Dropped",  
    width=40,
    height=5,
    bg="lightgray",
    anchor="center",        # Align text to the left inside the label
    justify="center",    # Align multiline text to the left
    font=("Arial", 12)
)
FileDropped.grid(padx=10, pady=10,row=1, column=1,sticky="nesw")

def Update_Spreadsheet():
    global data
    try:
        if Orientation.get() == "Unknown":
            raise Exception("Orientation is unknown. Please select it before updating the spreadsheet.")
        gc = gspread.service_account(filename="DatabaseWriter/qaproject-441416-f5fec0c61099.json")
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1pbH3O7yJwCc05Ktlb643T3rXZsN-EqXcTJfmnz37FU0/edit?gid=0#gid=0")
        values_list = sh.worksheet("Data").col_values(1)
        all_rows = sh.worksheet("Data").get_all_values()
        LastRow = len(values_list)+1

        Row = []
        Row.append(data["date_scanned"].strftime("%d-%m-%Y %H:%M:%S"))
        Row.append(data["data_analysed"].strftime("%d-%m-%Y %H:%M:%S"))

        def CheckIfNeedingUserInput(title,prompt):
            USER_INP = simpledialog.askstring(title=title,prompt=prompt)
            if USER_INP == None:
                raise ValueError("User cancelled the operation.")
            elif USER_INP == "":
                raise ValueError("User input is required for this field.")
            else:
                return USER_INP

        if data["ScannerDetails"]["Manufacturer"] == None:
            Row.append(CheckIfNeedingUserInput("Input Required", "Manufacturer is missing from the DICOM data. Please enter it now:"))
        else:
            Row.append(data["ScannerDetails"]["Manufacturer"])
        
        if data["ScannerDetails"]["Institution Name"] == None:
            Row.append(CheckIfNeedingUserInput("Input Required", "Institution Name is missing from the DICOM data. Please enter it now:"))
        else:
            Row.append(data["ScannerDetails"]["Institution Name"])

        if data["ScannerDetails"]["Model Name"] == None:
            Row.append(CheckIfNeedingUserInput("Input Required", "Model Name is missing from the DICOM data. Please enter it now:"))
        else:
            Row.append(data["ScannerDetails"]["Model Name"])
            
        if data["ScannerDetails"]["Serial Number"] == None:
            Row.append(CheckIfNeedingUserInput("Input Required", "Serial Number is missing from the DICOM data. Please enter it now:"))
        else:
            Row.append(data["ScannerDetails"]["Serial Number"])
        
        Row.append(data["Sequence"])
        Row.append(data["DICOM"][0].MagneticFieldStrength)

        #SNR
        if (type(data["Test"]["SNR"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SNR"].results["measurement"]["snr by smoothing"]["measured"])
            Row.append(data["Test"]["SNR"].results["measurement"]["snr by smoothing"]["normalised"])
        else:
            Row.append("Not Run")
            Row.append("Not Run")

        #GeoDist
        ExpectedSize = (data["ToleranceTable"]["Geometric Accuracy"]["MagNetMethod"].max + data["ToleranceTable"]["Geometric Accuracy"]["MagNetMethod"].min)/2.0
        if ExpectedSize != 85.0 or ExpectedSize != 80.0:
            ValueError("Warning", "The expected size for Geometric Distortion is not the standard 85mm or 80mm. Please check your tolerance table.")

        if (type(data["Test"]["GeoDist"]) != MedACRModules.Empty_Module.EmptyModule):
            #This needs tested
            HorDist = [0,0,0]
            HorDist[0] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][0]-ExpectedSize
            HorDist[1] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][1]-ExpectedSize
            HorDist[2] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][2]-ExpectedSize
            VertDist = [0,0,0]
            VertDist[0] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][0]-ExpectedSize
            VertDist[1] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][1]-ExpectedSize
            VertDist[2] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][2]-ExpectedSize
            if HorDist[0] > 8 and HorDist[0] < 12:
                if HorDist[1] > 8 and HorDist[1] < 12:
                    if HorDist[2] > 8 and HorDist[2] < 12:
                        if VertDist[0] > 8 and VertDist[0] < 12:
                            if VertDist[1] > 8 and VertDist[1] < 12:
                                if VertDist[2] > 8 and VertDist[2] < 12:
                                    result = messagebox.askquestion("Adjust distortion values?", "The distortion is large.\n Was the phantom one with 90mm pegs used?\n If so the distortion will be adjusted by 10mm.", icon='warning')
                                    if result == 'yes':
                                        HorDist[0] -=10
                                        HorDist[1] -=10
                                        HorDist[2] -=10
                                        VertDist[0] -=10
                                        VertDist[1] -=10
                                        VertDist[2] -=10
                                    else:
                                        FileDropped.config(text="No File Dropped")
                                        StandardLabel.config(bg="lightgray",text="No File Dropped")
                                        for item in tree.get_children():
                                            tree.delete(item)
                                        raise ValueError("error", "User cancelled operation due to large geometric distortion values.")
            Row.append(HorDist[0])
            Row.append(HorDist[1])
            Row.append(HorDist[2])
            Row.append(VertDist[0])
            Row.append(VertDist[1])
            Row.append(VertDist[2])
        else:
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")

        #Uniformity
        if (type(data["Test"]["Uniformity"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["Uniformity"].results["measurement"]["integral uniformity %"])
        else:
            Row.append("Not Run")

        #Ghosting
        if (type(data["Test"]["Ghosting"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["Ghosting"].results["measurement"]["signal ghosting %"])
        else:
            Row.append("Not Run")

        #Slice Pos
        if (type(data["Test"]["SlicePos"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SlicePos"].results['measurement'][data["Test"]["SlicePos"].results['file'][0]]['length difference'])
            Row.append(data["Test"]["SlicePos"].results['measurement'][data["Test"]["SlicePos"].results['file'][1]]['length difference'])
        else:
            Row.append("Not Run")
            Row.append("Not Run")

        #Slice Thickness
        if (type(data["Test"]["SliceThickness"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SliceThickness"].results["measurement"]["slice width mm"])
        else:
            Row.append("Not Run")

        #Spatial Res
        if (type(data["Test"]["SpatialRes"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(str(data["Test"]["SpatialRes"].settings["SpatialResMethod"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.1mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.0mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.9mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.8mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.1mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.0mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.9mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.8mm holes Vertical"]))
        else:
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
        Row.append(Coil.get())
        Row.append(Weighting.get())
        Row.append(Orientation.get())
        
        

        for entry in Row:
            if type(entry) != str:
                Row[Row.index(entry)] = str(round(entry,2))

        for row in all_rows:
            if row == Row:
                raise ValueError("This entry already exists in the database!")
        sh.worksheet("Data").update( values=[Row],range_name="A"+str(LastRow))
        messagebox.showinfo(title="Success",message="Spreadsheet updated!")

    except Exception as e:
        messagebox.showerror("Exception raised",message = str(repr(e)))

    FileDropped.config(text="No File Dropped")
    StandardLabel.config(bg="lightgray",text="No File Dropped")
    for item in tree.get_children():
        tree.delete(item)

OptionsFrame = tk.Frame(root, width=350, height=100)
OptionsFrame.grid(padx=10, pady=0,row=2, column=1,sticky="n")

WeightingFrame = tk.Frame(OptionsFrame, width=50, height=100)

WeightingLabels = tk.Label(WeightingFrame,text="Weighting").pack(side = TOP, ipady = 5, anchor=W) 
for (text, value) in {"T1" : "T1", "T2" : "T2"} .items(): 
    Radiobutton(WeightingFrame, text = text, variable = Weighting, 
        value = value).pack(side = TOP, ipady = 5,ipadx=10, anchor=W) 
WeightingFrame.grid(padx=10, pady=0,row=0, column=0,sticky="nw")

CoilFrame = tk.Frame(OptionsFrame, width=50, height=100)
CoilLabels = tk.Label(CoilFrame,text="Coil").pack(side = TOP, ipady = 5, anchor=N) 
for (text, value) in {"Head" : "Head", "Body AA" : "Body AA", "Head T/R" : "Head T/R","Integrated Body":"Integrated Body"} .items(): 
    Radiobutton(CoilFrame, text = text, variable = Coil, 
        value = value).pack(side = TOP, ipady = 0,ipadx=10, anchor=W) 
CoilFrame.grid(padx=10, pady=0,row=0, column=1,sticky="nw")

OrientationFrame = tk.Frame(OptionsFrame, width=50, height=100)
OrientationLabels = tk.Label(OrientationFrame,text="Orientation").pack(side = TOP, ipady = 5, anchor=N) 
for (text, value) in {"Axial" : "Axial", "Sagittal" : "Sagittal", "Coronal":"Coronal"} .items(): 
    Radiobutton(OrientationFrame, text = text, variable = Orientation, 
        value = value).pack(side = TOP, ipady = 0,ipadx=10, anchor=W) 
OrientationFrame.grid(padx=10, pady=0,row=0, column=2,sticky="nw")

UpdateSpread = tk.Button(root, text="Update Spreadsheet", command=Update_Spreadsheet)
UpdateSpread.grid(padx=10, pady=5,row=3, column=1,sticky="nesw")
UpdateSpread.config(state="disabled")

columns = ("Paramater","Standard", "DICOM", "Match?")
tree = ttk.Treeview(root, columns=columns, show="headings",height=14)

style = ttk.Style()
style.configure("Treeview.Heading", foreground="red", font=("Arial", 10, "bold"))

for col in columns:
    tree.heading(col, text=col)
tree.column("Paramater", width=150)
tree.column("Standard", width=80)
tree.column("DICOM", width=80)
tree.column("Match?", width=80)

tree.grid(padx=10, pady=10,row=1, column=0,sticky="sw",rowspan=3)

def drop(event):
    global data
    files = root.tk.splitlist(event.data)
    UpdateSpread.config(state="disabled")
    if len(files) == 1:
        with open(files[0], 'rb') as f:
            data = pickle.load(f)
            result,resultDict = StandardConfirmation.CheckAgainstStandard(data,Weighting.get())
            if result == True:
                StandardLabel.config(bg="green",text="File meets the standard: \N{Check Mark}")
                UpdateSpread.config(state="normal")
            else:
                StandardLabel.config(bg="red",text="File doesn't meet the standard: \N{Box Drawings Light Diagonal Cross}")

            for i in tree.get_children():
                tree.delete(i)

            FileDropped.config(text="File Dropped:\n" + os.path.basename(files[0]))

            for key in resultDict:
                tree.insert("", tk.END, values=(str(key),str(resultDict[key][0]),str(resultDict[key][1]),str(resultDict[key][2])))

    else:
        messagebox.showwarning("Warning", "You dropped More Than One File!")

    Orientation.set("Unknown")
    if "ax" in data["Sequence"].lower():
        Orientation.set("Axial")
    if "tra" in data["Sequence"].lower():
        Orientation.set("Axial")
    elif "sag" in data["Sequence"].lower():
        Orientation.set("Sagittal")
    elif "cor" in data["Sequence"].lower():
        Orientation.set("Coronal")
    
    if Orientation.get() == "Unknown":
        messagebox.showwarning("Warning", "Could not determine orientation from sequence name. Please select it manually.")

# Bind the drop event to the label
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

root.mainloop()