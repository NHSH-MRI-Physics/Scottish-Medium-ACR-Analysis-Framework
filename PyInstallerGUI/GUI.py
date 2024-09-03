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

    def ResetWindowing():
        VarHolder.WidthChange = 0
        VarHolder.LevelChange = 0
        BaseVmax = np.max(VarHolder.CurrentImage)
        BaseVmin = np.min(VarHolder.CurrentImage)
        VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
        VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0
        VarHolder.WinLevelLabel.config(text = "Window Level: " + str(VarHolder.CurrentLevel))
        VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(VarHolder.CurrentWidth))
        plot()
        VarHolder.Canvas.draw()

    def SubmitPoints():
        if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[0]) == 4 and len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[0]) == 4:
            if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[1]) == 4 and len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[1]) == 4:
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[0]) == 3 and len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[0]) == 3:
                    if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[1]) == 3 and len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[1]) == 3:
                        VarHolder.NewWindow.destroy()
                        return
        messagebox.showinfo("error", "There must be 4 peaks (crosses) and 3 (circles) troughs horizontal (blue) and vertical (red) points chosen.")

    def on_click_on_plot(event):
        if event.inaxes is not None:
            if event.button == 1 and VarHolder.ShiftPressed == False:
                VarHolder.ManualResData[VarHolder.CurrentROI].HoleSize = VarHolder.CurrentROI
                VarHolder.ManualResData[VarHolder.CurrentROI].Image = VarHolder.CurrentImage
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) + len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction]) <7:
                    if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) < 4:
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction].append( (event.xdata))
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction].append( (event.ydata))
                        Marker = "x"
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[0],linestyle='' ,marker=Marker,color="blue")
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[1],linestyle='' ,marker=Marker,color="red")
                    #elif len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) > 4:
                    else:
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction].append( (event.xdata))
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction].append( (event.ydata))
                        Marker="o"
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[0],linestyle='', marker=Marker,color="blue")
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[1],linestyle='', marker=Marker,color="red")
                    
                    VarHolder.Canvas.draw()


            elif event.button == 1 and VarHolder.ShiftPressed == True:
                DistancesPeak = []
                for i in range(len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction])):
                    DistancesPeak.append( (event.xdata - VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction][i])**2 + (event.ydata - VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction][i])**2)
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) >0:
                    IndexOfClosestPeak = np.argmin(DistancesPeak)

                DistancesTrough = []
                for i in range(len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction])):
                    DistancesTrough.append( (event.xdata - VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction][i])**2 + (event.ydata - VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction][i])**2)
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction]) >0:
                    IndexOfClosestTrough = np.argmin(DistancesTrough)
                
                DonePeaks = False
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) >0:
                    if DistancesPeak[IndexOfClosestPeak] < 0.1:
                        del VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction][IndexOfClosestPeak]
                        del VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction][IndexOfClosestPeak]
                        
                        if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) >0:
                            if VarHolder.Direction==0:
                                VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction])))
                            elif VarHolder.Direction ==1:
                                VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction])))

                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction] = list(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction])
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction] = list(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction])
                        
                        plt.clf()
                        plt.title(VarHolder.CurrentROI) 
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
                        
                        Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
                        Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth
                        plot(Vmin=Vmin,Vmax=Vmax)

                        VarHolder.Canvas.draw()
                        DonePeaks=True

                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction]) >0:
                    if DistancesTrough[IndexOfClosestTrough] < 0.1 and DonePeaks==False:
                        del VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction][IndexOfClosestTrough]
                        del VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction][IndexOfClosestTrough]
                        
                        if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction]) >0:
                            if VarHolder.Direction==0:
                                VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction])))
                            elif VarHolder.Direction ==1:
                                VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction])))

                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction] = list(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction])
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction] = list(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction])
                        
                        plt.clf()
                        plt.title(VarHolder.CurrentROI) 
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
                        plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
                        
                        Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
                        Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth
                        plot(Vmin=Vmin,Vmax=Vmax)
                        VarHolder.Canvas.draw()

    def DetectShiftPress(event):
        if event.key == 'shift':
            VarHolder.ShiftPressed = True
        if event.key == "control" :
            VarHolder.Direction = 1
            VarHolder.WinDirectionLabel.config(text = "Current Direction: Vertical")
        if event.key == "ctrl+shift" or event.key == "shift+control":
            VarHolder.ShiftPressed = True
            VarHolder.Direction = 1
            VarHolder.WinDirectionLabel.config(text = "Current Direction: Vertical")

    def DetectShiftReleased(event):
        if event.key == 'shift':
            VarHolder.ShiftPressed = False
        if event.key == "control":
            VarHolder.Direction = 0
            VarHolder.WinDirectionLabel.config(text = "Current Direction: Horizontal")
        if event.key == "ctrl+shift" or event.key == "shift+control":
            VarHolder.ShiftPressed = False
            VarHolder.Direction = 0
            VarHolder.WinDirectionLabel.config(text = "Current Direction: Horizontal")

        if event.key == "alt":
            print("Automatically fitting troughs..")
            for Direction in range(2):
                if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[Direction]) == 4:
                    if Direction==0:
                        SortedXPeaks, SortedYPeaks = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[Direction])))
                    else:
                        SortedYPeaks, SortedXPeaks = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[Direction])))

                    VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[Direction] = []
                    VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[Direction] = []

                    for idx in range(3):
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[Direction].append( (SortedXPeaks[idx] + SortedXPeaks[idx+1])/2.0 )
                        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[Direction].append( (SortedYPeaks[idx] + SortedYPeaks[idx+1])/2.0 )

            plt.clf()
            plt.title(VarHolder.CurrentROI) 
            plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
            plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
            plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[0], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
            plt.plot(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[1], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
            
            Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
            Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth
            plot(Vmin=Vmin,Vmax=Vmax)
            VarHolder.Canvas.draw()


            #SortedYPeaks, SortedXPeaks = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction])))

    def ManualRes(ROIS):
        for key in ROIS:
            VarHolder.ManualResData[key] = VariableHolder.ManualResData()
            VarHolder.CurrentROI=key
            print ("Displaying Res Pattern: " +key)
            VarHolder.NewWindow =  tkinter.Toplevel(root)
            VarHolder.NewWindow.iconbitmap("_internal\ct-scan.ico")
            VarHolder.NewWindow.geometry("500x540")
            VarHolder.NewWindow.configure(background='white')
            VarHolder.NewWindow.resizable(False,False)
            plt.title(key) 
            VarHolder.CurrentImage = ROIS[key]
            BaseVmax = np.max(VarHolder.CurrentImage)
            BaseVmin = np.min(VarHolder.CurrentImage)
            VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
            VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0
            plot()
            VarHolder.Canvas = FigureCanvasTkAgg(plt.gcf(), master = VarHolder.NewWindow)   
            plt.gcf().canvas.callbacks.connect('button_press_event', on_click_on_plot)
            plt.gcf().canvas.callbacks.connect('key_press_event', DetectShiftPress)
            plt.gcf().canvas.callbacks.connect('key_release_event', DetectShiftReleased)

            VarHolder.Canvas.draw() 
            VarHolder.Canvas.get_tk_widget().pack(side=TOP)
            toolbar = NavigationToolbar2Tk(VarHolder.Canvas, VarHolder.NewWindow) 
            toolbar.update() 
            VarHolder.Canvas.get_tk_widget().pack() 

            SubmitPointsBtn = ttk.Button(VarHolder.NewWindow, text="Submit",width=10, command =SubmitPoints)
            SubmitPointsBtn.place(relx=0.11, rely=0.89, anchor="center")

            ResetWindowingBtn = ttk.Button(VarHolder.NewWindow, text="Reset Windowing",width=20, command =ResetWindowing)
            ResetWindowingBtn.place(relx=0.4, rely=0.89, anchor="center")

            VarHolder.WinDirectionLabel = ttk.Label(VarHolder.NewWindow, text="Current Direction: Horizontal", background="white", foreground="black")
            VarHolder.WinDirectionLabel.place(relx=0.3, rely=0.85,anchor="center")

            VarHolder.WinLevelLabel = ttk.Label(VarHolder.NewWindow, text="Window Level: " + str(VarHolder.CurrentLevel), background="white", foreground="black")
            VarHolder.WinLevelLabel.place(relx=0.8, rely=0.86,anchor="center")

            VarHolder.WinWidthLabel = ttk.Label(VarHolder.NewWindow, text="Window Width: "+ str(VarHolder.CurrentWidth), background="white", foreground="black")
            VarHolder.WinWidthLabel.place(relx=0.8, rely=0.90,anchor="center")

            VarHolder.NewWindow.bind("<ButtonPress-3>", StartTracking)
            VarHolder.NewWindow.bind("<ButtonRelease-3>", EndTracking)
            VarHolder.NewWindow.bind("<B3-Motion>", Windowing_handler)

            

            root.wait_window(VarHolder.NewWindow)
            plt.close()

    def Windowing_handler(event):
        if VarHolder.StartingEvent != None:
            Delta = datetime.datetime.now() - VarHolder.TimeOfLastEvent
            if (Delta.total_seconds() > 0.0001):
                VarHolder.WidthChange = event.x - VarHolder.StartingEvent.x
                VarHolder.LevelChange = VarHolder.StartingEvent.y - event.y  
                TempCurrentLevel = VarHolder.CurrentLevel + VarHolder.LevelChange
                TempCurrentWidth = VarHolder.CurrentWidth + VarHolder.WidthChange
                if TempCurrentWidth <0:
                    TempCurrentWidth = 0

                VarHolder.WinLevelLabel.config(text = "Window Level: " + str(TempCurrentLevel))
                VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(TempCurrentWidth))

                #We need to remove the current change, if we do not every step we add more to the taacker. Eg: Step 1 +1 step 2 +2 meaning wihtout the removal we get +3 instead of the intended +2
                TempCurrentLevel -= (VarHolder.LevelChange)
                TempCurrentWidth -= (VarHolder.WidthChange)

                VarHolder.TimeOfLastEvent = datetime.datetime.now()
    
    def StartTracking(event):
        VarHolder.StartingEvent=event

    def EndTracking(event):
        VarHolder.StartingEvent=None
        VarHolder.CurrentLevel = VarHolder.CurrentLevel + VarHolder.LevelChange
        VarHolder.CurrentWidth = VarHolder.CurrentWidth + VarHolder.WidthChange
        if VarHolder.CurrentWidth <0:
            VarHolder.CurrentWidth = 0
        
        Vmin = VarHolder.CurrentLevel - VarHolder.CurrentWidth
        Vmax = VarHolder.CurrentLevel + VarHolder.CurrentWidth

        plot(Vmin=Vmin,Vmax=Vmax)
        VarHolder.Canvas.draw()


    def plot(Vmin=None,Vmax=None):
        if Vmin != None and Vmax != None:
            plt.imshow(VarHolder.CurrentImage,cmap="gray",vmin=Vmin,vmax=Vmax)
        else:
            plt.imshow(VarHolder.CurrentImage,cmap="gray")

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


            #DEBUGGING STUFF
            #del ROIS[list(ROIS.keys())[1]]
            #del ROIS[list(ROIS.keys())[1]]
            #del ROIS[list(ROIS.keys())[1]]

            plt.close('all')#Making sure no rogue plots are sitting in the background...
            ManualRes(ROIS)
            MedACRAnalysis.ManualResData = VarHolder.ManualResData
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