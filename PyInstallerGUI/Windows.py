import tkinter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW
import pydicom
from pydicom.filereader import read_dicomdir
from pydicom import dcmread
import glob
import os 
from enum import Enum
import math
from tkinter import ttk
import numpy as np
from hazenlib.ACRObject import ACRObject
import MedACRAnalysisV2
import VariableHolder
import datetime


def GetDICOMS(dicomPath,seq):
    '''
    files = glob.glob(os.path.join(dicomPath,"*"))
    Dcms = []
    for file in files: 
        try:
            dicom = dcmread(file)
            if dicom.SeriesDescription == seq:
                Dcms.append(dicom)
        except:
            print ("WARNING: " + file + " was not able to be loaded, this file will be skipped!")
    '''
    Dcms = MedACRAnalysisV2.DICOM_Holder_Dict[seq]
    Options = {}
    Options["MediumACRPhantom"] = True
    AcrObj = ACRObject(Dcms.DICOM_Data,Options)
    Dcms = AcrObj.dcms

    plt.imshow(Dcms[0].pixel_array)
    plt.savefig("test.png")

    return Dcms,AcrObj
        

class CentreRadiusMaskingWindow():
    def __init__(self,root,dicomPath,seq,overridemasking = False, slice=7,PreCalcdCentre = None):
        slice -=1 #Convert it back to index that starts at 0
        self.points = []
        self.Centrex = None
        self.Centrey = None
        self.Radius = None
        self.Mask = None
        self.PreCalcdCentre = PreCalcdCentre
        '''
        files = glob.glob(os.path.join(dicomPath,"*"))
        Dcms = []
        for file in files: 
            try:
                dicom = dcmread(file)
                if dicom.SeriesDescription == seq:
                    Dcms.append(dicom)
            except:
                print ("WARNING: " + file + " was not able to be loaded, this file will be skipped!")
        self.Dcms = sorted(Dcms, key=lambda d: d.SliceLocation)
        '''
        self.Dcms,__ = GetDICOMS(dicomPath,seq) #This is a better way of doing it, it just uses the ACRobject to make sure the ortientations etc are correct
        self.root = root
        self.Title = "Displaying Slice " + str(slice+1) + "\nChoose 4 points on the edge of the circle"
        self.overrideMasking = overridemasking
        self.slice = slice

    def  on_click_on_plot(self,event):
        if (self.canvas.toolbar.mode) != '':
            return

        if event.button == 1:
            if event.xdata == None or event.ydata == None:
                return

            if len(self.points) < 4:
                self.points.append((event.xdata, event.ydata))

            plt.clf()
            plt.imshow(self.Image, cmap='gray')
            if self.PreCalcdCentre != None:
                plt.plot(self.PreCalcdCentre[0],self.PreCalcdCentre[1],marker="x",color="red")
            plt.title(self.Title)
            for point in self.points:
                plt.plot(point[0],point[1],'ro')

            if len(self.points) == 4:
                import circle_fit as cf
                self.Centrex,self.Centrey,self.Radius,_ = cf.least_squares_circle((self.points))
                
                t = np.linspace(0, 2 * np.pi, 1000, endpoint=True)
                circle1 = plt.Circle((self.Centrex, self.Centrey), self.Radius, color='r',fill=False)
                plt.gca().add_patch(circle1)

                if self.overrideMasking == True:
                    self.Mask = np.zeros(self.Image.shape)
                    for i in range(self.Image.shape[0]):
                        for j in range(self.Image.shape[1]):
                            if math.sqrt((i - self.Centrex)**2 + (j - self.Centrey)**2) < self.Radius:
                                self.Mask[j,i] = 1
                    plt.imshow(self.Mask,alpha = 0.4)

            self.canvas.draw() 

        if event.button == 3:
            DeleteDistance = 5
            distances = []
            for point in self.points:
                distances.append(math.sqrt((point[0] - event.xdata)**2 + (point[1] - event.ydata)**2))
            min_index = np.argmin(distances)

            if distances[min_index] <= DeleteDistance:
                del self.points[min_index]

                plt.clf()
                plt.imshow(self.Image, cmap='gray')
                plt.title(self.Title)
                if self.PreCalcdCentre != None:
                    plt.plot(self.PreCalcdCentre[0],self.PreCalcdCentre[1],marker="x",color="red")
                for point in self.points:
                    plt.plot(point[0],point[1],'ro')    
                self.canvas.draw()         
            

    def Reset(self):
        plt.clf()
        plt.imshow(self.Image, cmap='gray')
        if self.PreCalcdCentre != None:
            plt.plot(self.PreCalcdCentre[0],self.PreCalcdCentre[1],marker="x",color="red")
        plt.title(self.Title)
        self.canvas.draw() 
        self.Centrex = None
        self.Centrey = None
        self.Radius = None
        self.Mask = None
        self.points = []

    def Submit(self,Window):
        if len(self.points) != 4:
            messagebox.showerror("Error", "Please select 4 points non the edge of the circle")
            return        
        plt.clf()
        self.Centrex = int(round(self.Centrex,0))
        self.Centrey = int(round(self.Centrey,0))
        self.Radius = int(round(self.Radius,0))
        if self.PreCalcdCentre != None:
            if self.overrideMasking == True:
                if self.Mask[self.PreCalcdCentre[1],self.PreCalcdCentre[0]] == 0:
                    messagebox.showerror("Error", "mask does not contain the centre of the phantom ")
                    self.Reset()
                    return
        Window.destroy()

    def GetCentreRadiusMask(self):
        plt.close('all')
        Win = tkinter.Toplevel(self.root)
        Win.iconbitmap("_internal\ct-scan.ico")
        Win.geometry("500x540")

        def disable_event():
            pass
        Win.protocol("WM_DELETE_WINDOW", disable_event)

        Win.configure(background='white')
        Win.resizable(False,False)

        plt.title(self.Title)
        self.Image = self.Dcms[self.slice].pixel_array
        plt.imshow(self.Image, cmap='gray')
        if self.PreCalcdCentre != None:
            plt.plot(self.PreCalcdCentre[0],self.PreCalcdCentre[1],marker="x",color="red")
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master = Win) 
        plt.gcf().canvas.callbacks.connect('button_press_event', self.on_click_on_plot)
        self.canvas.draw() 
        self.canvas.get_tk_widget().pack(side=TOP)
        toolbar = NavigationToolbar2Tk(self.canvas, Win) 
        toolbar.update() 
        self.canvas.get_tk_widget().pack() 

        ResetButton = ttk.Button(Win,text="Reset",width=22,command=self.Reset)
        ResetButton.place(relx=0.25, rely=0.89, anchor='center')

        ResetButton = ttk.Button(Win,text="Submit",width=22,command=lambda: self.Submit(Win))
        ResetButton.place(relx=0.75, rely=0.89, anchor='center')

        self.root.wait_window(Win)


class GetROIOfResBlock():
    def __init__(self,root,dicomPath,seq):
        self.root = root
        self.Dcms, ACR_obj = GetDICOMS(dicomPath,seq) #This is a better way of doing it, it just uses the ACRobject to make sure the ortientations etc are correct
        self.FixedSize=True
        self.MakingRect = False
        self.Rect = [None,None,None,None]
        self.SelectedRects = [None,None,None,None]
        self.Size = [18.19/ACR_obj.pixel_spacing[0],16.67/ACR_obj.pixel_spacing[0],15.73/ACR_obj.pixel_spacing[0],13.30/ACR_obj.pixel_spacing[0]]

        self.colours = [ "red", "green", "blue", "yellow"]
        self.ResTitle = ["1.1mm","1.0mm", "0.9mm", "0.8mm"]
        self.RectID = 0
        self.crops = [None,None,None,None]

    def Reset(self):
        self.Rect = [None,None,None,None]
        for i in range(4):
            if self.SelectedRects[i] != None:
                self.SelectedRects[i].remove()
        self.SelectedRects = [None,None,None,None]
        self.RectID = 0
        plt.title("Draw a box around the " + str(self.ResTitle[self.RectID])+" grid")
        self.canvas.draw() 
        
    def Submit(self,Window):
        for rect in self.SelectedRects:
            if rect == None:
                messagebox.showerror("Error", "Please draw a box round all 4 resolution grids")
                return

        def get_rectangle_center(rect):
            x0, y0 = rect.get_xy()
            x1 = x0 + rect.get_width()
            center_x = (x0 + x1) / 2
            return center_x
        OrderedRect = sorted(self.SelectedRects, key=lambda rect: get_rectangle_center(rect))

        #keys = list(self.crops.keys())
        for i in range(4):
            rect = OrderedRect[i]
            #print(i,rect.get_xy(), rect.get_xy()[0] + rect.get_width(),rect.get_xy()[1] + rect.get_height())
            x0, y0 = rect.get_xy()
            x1 = x0 + rect.get_width()
            y1 = y0 + rect.get_height()
            if rect.get_width() >= 0:
                x0,x1 = int(math.floor(x0)), int(math.ceil(x1))
            else:
                x1,x0 = int(math.ceil(x0)), int(math.floor(x1))

            if rect.get_height() >= 0:
                y0,y1 = int(math.floor(y0)), int(math.ceil(y1))
            else:
                y1,y0 = int(math.ceil(y0)), int(math.floor(y1))

            #x0, y0, x1, y1 = int(math.floor(x0)), int(math.floor(y0)), int(math.ceil(x1))+1, int(math.ceil(y1))+1
            self.crops[i] = self.Image[y0:y1, x0:x1]
            #self.Image[y0:y1, x0:x1] = 0
            plt.imshow(self.Image,cmap="gray")
            self.canvas.draw()   

        #Make Crops and return them
        Window.destroy()

    def onmove(self,event):
        if event.xdata == None or event.ydata == None:
                return

        if self.MakingRect == True:
            if self.SelectedRects[self.RectID] != None:
                self.SelectedRects[self.RectID].remove()
            self.Rect[2] = event.xdata
            self.Rect[3] = event.ydata
            self.SelectedRects[self.RectID] = plt.Rectangle((self.Rect[0],self.Rect[1]),self.Rect[2]-self.Rect[0],self.Rect[3]-self.Rect[1],color=self.colours[self.RectID],fill=False)
            plt.gca().add_patch(self.SelectedRects[self.RectID])
            self.canvas.draw()   

    def on_click_on_plot(self,event):
        if (self.canvas.toolbar.mode) != '':
            return
        if event.button == 1 and self.RectID < 4:
            self.MakingRect=True
            self.Rect[0] = event.xdata
            self.Rect[1] = event.ydata

        if event.button == 3:
            for i in range(4):
                if self.SelectedRects[i] != None:
                    rect = self.SelectedRects[i]
                    x0, y0 = rect.get_xy()
                    x1 = x0 + rect.get_width()
                    y1 = y0 + rect.get_height()

                    if rect.get_width() < 0:
                        xtemp = x1
                        x1 = x0
                        x0 = xtemp

                    if rect.get_height() < 0:
                        ytemp = y1
                        y1 = y0
                        y0 = ytemp

                    if x0 <= event.xdata <= x1 and y0 <= event.ydata <= y1:
                        self.SelectedRects[i].remove()
                        self.SelectedRects[i] = None
                        self.RectID = self.SelectedRects.index(None)
              
            plt.title("Draw a box around the " + str(self.ResTitle[self.RectID])+" grid")
            self.canvas.draw() 

    def release_click_on_plot(self,event):
        if self.MakingRect == True:
            self.MakingRect=False
            if None in self.SelectedRects:
                self.RectID = self.SelectedRects.index(None)
            else:
                self.RectID = 4
            if self.RectID<=3:
                plt.title("Draw a box around the " + str(self.ResTitle[self.RectID])+" grid")
                self.canvas.draw() 
            else:
                plt.title("All boxes drawn")
                self.canvas.draw() 

    def release_click_on_plot_FixedSize(self,event):
        x = event.xdata
        y = event.ydata

        if (self.canvas.toolbar.mode) != '':
            return
        
        if event.button == 1 and self.RectID < 4:
            self.SelectedRects[self.RectID] = plt.Rectangle( (x-self.Size[self.RectID]/2.0,y-self.Size[self.RectID]/2.0),self.Size[self.RectID],self.Size[self.RectID],color=self.colours[self.RectID],fill=False)
            plt.gca().add_patch(self.SelectedRects[self.RectID])
            self.canvas.draw()   
            if None in self.SelectedRects:
                    self.RectID = self.SelectedRects.index(None)
            else:
                self.RectID = 4
            if self.RectID<=3:
                plt.title("Click the centre of the " + str(self.ResTitle[self.RectID])+" grid")
                self.canvas.draw() 
            else:
                plt.title("All boxes drawn")
                self.canvas.draw() 
        
        if event.button == 3:
            for i in range(4):
                if self.SelectedRects[i] != None:
                    rect = self.SelectedRects[i]
                    x0, y0 = rect.get_xy()
                    x1 = x0 + rect.get_width()
                    y1 = y0 + rect.get_height()

                    if rect.get_width() < 0:
                        xtemp = x1
                        x1 = x0
                        x0 = xtemp

                    if rect.get_height() < 0:
                        ytemp = y1
                        y1 = y0
                        y0 = ytemp

                    if x0 <= event.xdata <= x1 and y0 <= event.ydata <= y1:
                        self.SelectedRects[i].remove()
                        self.SelectedRects[i] = None
                        self.RectID = self.SelectedRects.index(None)
                        plt.title("Draw a box around the " + str(self.ResTitle[self.RectID])+" grid")
                        self.canvas.draw() 


    def GetROIs(self):
        plt.close('all')
        Win = tkinter.Toplevel(self.root)
        Win.iconbitmap("_internal\ct-scan.ico")
        Win.geometry("500x540")
        Win.configure(background='white')
        Win.resizable(False,False)

        def disable_event():
            pass
        Win.protocol("WM_DELETE_WINDOW", disable_event)
        plt.title("Draw a box around the " + str(self.ResTitle[self.RectID])+" grid")
        self.Image = self.Dcms[0].pixel_array
        plt.imshow(self.Image,cmap="gray")
        self.canvas = FigureCanvasTkAgg(plt.gcf(), master = Win) 

        if self.FixedSize == False:
            plt.gcf().canvas.callbacks.connect('button_press_event', self.on_click_on_plot)
            plt.gcf().canvas.callbacks.connect('button_release_event', self.release_click_on_plot)
            plt.gcf().canvas.callbacks.connect("motion_notify_event", self.onmove)
        else:
            plt.gcf().canvas.callbacks.connect('button_release_event', self.release_click_on_plot_FixedSize)
        
        self.canvas.draw() 
        self.canvas.get_tk_widget().pack(side=TOP)
        toolbar = NavigationToolbar2Tk(self.canvas, Win) 
        toolbar.update() 
        self.canvas.get_tk_widget().pack() 

        ResetButton = ttk.Button(Win,text="Reset",width=22,command=self.Reset)
        ResetButton.place(relx=0.25, rely=0.89, anchor='center')

        ResetButton = ttk.Button(Win,text="Submit",width=22,command=lambda: self.Submit(Win))
        ResetButton.place(relx=0.75, rely=0.89, anchor='center')

        self.root.wait_window(Win)

class ManualResWindow():
    def __init__(self,root):
        self.root = root
        self.VarHolder=VariableHolder.VarHolder()

    def ManualRes(self,ROIS):
        for key in ROIS:
            self.VarHolder.ManualResData[key] = VariableHolder.ManualResData()
            self.VarHolder.CurrentROI=key
            print ("Displaying Res Pattern: " +key)
            self.VarHolder.NewWindow =  tkinter.Toplevel(self.root)
            self.VarHolder.NewWindow.iconbitmap("_internal\ct-scan.ico")
            self.VarHolder.NewWindow.geometry("500x560")
            self.VarHolder.NewWindow.configure(background='white')
            self.VarHolder.NewWindow.resizable(False,False)
            plt.title(key) 
            self.VarHolder.CurrentImage = ROIS[key]
            BaseVmax = np.max(self.VarHolder.CurrentImage)
            BaseVmin = np.min(self.VarHolder.CurrentImage)
            self.VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
            self.VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0
            self.plot()
            self.VarHolder.Canvas = FigureCanvasTkAgg(plt.gcf(), master = self.VarHolder.NewWindow)   
            plt.gcf().canvas.callbacks.connect('button_press_event', self.on_click_on_plot)
            plt.gcf().canvas.callbacks.connect('key_press_event', self.DetectShiftPress)
            plt.gcf().canvas.callbacks.connect('key_release_event', self.DetectShiftReleased)

            self.VarHolder.Canvas.draw() 
            self.VarHolder.Canvas.get_tk_widget().pack(side=TOP)
            toolbar = NavigationToolbar2Tk(self.VarHolder.Canvas, self.VarHolder.NewWindow) 
            toolbar.update() 
            self.VarHolder.Canvas.get_tk_widget().pack() 

            SubmitPointsBtn = ttk.Button(self.VarHolder.NewWindow, text="Submit",width=10, command = self.SubmitPoints)
            SubmitPointsBtn.place(relx=0.11, rely=0.89, anchor="center")

            ResetWindowingBtn = ttk.Button(self.VarHolder.NewWindow, text="Reset Windowing",width=20, command = self.ResetWindowing)
            ResetWindowingBtn.place(relx=0.4, rely=0.89, anchor="center")

            self.VarHolder.WinDirectionLabel = ttk.Label(self.VarHolder.NewWindow, text="Current Direction: Horizontal", background="white", foreground="black")
            self.VarHolder.WinDirectionLabel.place(relx=0.3, rely=0.82,anchor="center")

            self.VarHolder.WinLevelLabel = ttk.Label(self.VarHolder.NewWindow, text="Window Level: " + str(self.VarHolder.CurrentLevel), background="white", foreground="black")
            self.VarHolder.WinLevelLabel.place(relx=0.8, rely=0.86,anchor="center")

            self.VarHolder.WinWidthLabel = ttk.Label(self.VarHolder.NewWindow, text="Window Width: "+ str(self.VarHolder.CurrentWidth), background="white", foreground="black")
            self.VarHolder.WinWidthLabel.place(relx=0.8, rely=0.90,anchor="center")

            self.VarHolder.NewWindow.bind("<ButtonPress-3>", self.StartTracking)
            self.VarHolder.NewWindow.bind("<ButtonRelease-3>", self.EndTracking)
            self.VarHolder.NewWindow.bind("<B3-Motion>", self.Windowing_handler)

            def disable_event():
                pass
            self.VarHolder.NewWindow.protocol("WM_DELETE_WINDOW", disable_event)

            self.root.wait_window(self.VarHolder.NewWindow)
            plt.close()
        
        return self.VarHolder.ManualResData

    def Windowing_handler(self,event):
        if self.VarHolder.StartingEvent != None:
            Delta = datetime.datetime.now() - self.VarHolder.TimeOfLastEvent
            if (Delta.total_seconds() > 0.0001):
                self.VarHolder.WidthChange = event.x - self.VarHolder.StartingEvent.x
                self.VarHolder.LevelChange = self.VarHolder.StartingEvent.y - event.y  
                TempCurrentLevel = self.VarHolder.CurrentLevel + self.VarHolder.LevelChange
                TempCurrentWidth = self.VarHolder.CurrentWidth + self.VarHolder.WidthChange
                if TempCurrentWidth <0:
                    TempCurrentWidth = 0

                self.VarHolder.WinLevelLabel.config(text = "Window Level: " + str(TempCurrentLevel))
                self.VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(TempCurrentWidth))

                #We need to remove the current change, if we do not every step we add more to the taacker. Eg: Step 1 +1 step 2 +2 meaning wihtout the removal we get +3 instead of the intended +2
                TempCurrentLevel -= (self.VarHolder.LevelChange)
                TempCurrentWidth -= (self.VarHolder.WidthChange)

                self.VarHolder.TimeOfLastEvent = datetime.datetime.now()
    
    def StartTracking(self,event):
        self.VarHolder.StartingEvent=event

    def EndTracking(self,event):
        self.VarHolder.StartingEvent=None
        self.VarHolder.CurrentLevel = self.VarHolder.CurrentLevel + self.VarHolder.LevelChange
        self.VarHolder.CurrentWidth = self.VarHolder.CurrentWidth + self.VarHolder.WidthChange
        if self.VarHolder.CurrentWidth <0:
            self.VarHolder.CurrentWidth = 0
        
        Vmin = self.VarHolder.CurrentLevel - self.VarHolder.CurrentWidth
        Vmax = self.VarHolder.CurrentLevel + self.VarHolder.CurrentWidth

        self.plot(Vmin=Vmin,Vmax=Vmax)
        self.VarHolder.Canvas.draw()


    def plot(self,Vmin=None,Vmax=None):
        if Vmin != None and Vmax != None:
            plt.imshow(self.VarHolder.CurrentImage,cmap="gray",vmin=Vmin,vmax=Vmax)
        else:
            plt.imshow(self.VarHolder.CurrentImage,cmap="gray")

    def ResetWindowing(self):
        self.VarHolder.WidthChange = 0
        self.VarHolder.LevelChange = 0
        BaseVmax = np.max(self.VarHolder.CurrentImage)
        BaseVmin = np.min(self.VarHolder.CurrentImage)
        self.VarHolder.CurrentLevel = (BaseVmax+BaseVmin)/2.0
        self.VarHolder.CurrentWidth = (BaseVmax-BaseVmin)/2.0
        self.VarHolder.WinLevelLabel.config(text = "Window Level: " + str(self.VarHolder.CurrentLevel))
        self.VarHolder.WinWidthLabel.config(text = "Window Width: "+ str(self.VarHolder.CurrentWidth))
        self.plot()
        self.VarHolder.Canvas.draw()

    def SubmitPoints(self):
        if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[0]) == 4 and len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[0]) == 4:
            if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[1]) == 4 and len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[1]) == 4:
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[0]) == 3 and len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[0]) == 3:
                    if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[1]) == 3 and len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[1]) == 3:
                        self.VarHolder.NewWindow.destroy()
                        return
        messagebox.showinfo("error", "There must be 4 peaks (crosses) and 3 (circles) troughs horizontal (blue) and vertical (red) points chosen.")

    def on_click_on_plot(self,event):
        if event.inaxes is not None:
            if event.button == 1 and self.VarHolder.ShiftPressed == False:
                self.VarHolder.ManualResData[self.VarHolder.CurrentROI].HoleSize = self.VarHolder.CurrentROI
                self.VarHolder.ManualResData[self.VarHolder.CurrentROI].Image = self.VarHolder.CurrentImage
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction]) + len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction]) <7:
                    if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction]) < 4:
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction].append( (event.xdata))
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[self.VarHolder.Direction].append( (event.ydata))
                        Marker = "x"
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[0],linestyle='' ,marker=Marker,color="blue")
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[1],linestyle='' ,marker=Marker,color="red")
                    #elif len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) > 4:
                    else:
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction].append( (event.xdata))
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[self.VarHolder.Direction].append( (event.ydata))
                        Marker="o"
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[0],linestyle='', marker=Marker,color="blue")
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[1],linestyle='', marker=Marker,color="red")
                    
                    self.VarHolder.Canvas.draw()


            elif event.button == 1 and self.VarHolder.ShiftPressed == True:
                DistancesPeak = []
                for i in range(len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction])):
                    DistancesPeak.append( (event.xdata - self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction][i])**2 + (event.ydata - self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[self.VarHolder.Direction][i])**2)
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction]) >0:
                    IndexOfClosestPeak = np.argmin(DistancesPeak)

                DistancesTrough = []
                for i in range(len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction])):
                    DistancesTrough.append( (event.xdata - self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction][i])**2 + (event.ydata - self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[self.VarHolder.Direction][i])**2)
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction]) >0:
                    IndexOfClosestTrough = np.argmin(DistancesTrough)
                
                DonePeaks = False
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction]) >0:
                    if DistancesPeak[IndexOfClosestPeak] < 0.1:
                        del self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction][IndexOfClosestPeak]
                        del self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[self.VarHolder.Direction][IndexOfClosestPeak]
                        
                        #if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction]) >0:
                        #    if VarHolder.Direction==0:
                        #        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction])))
                        #    elif VarHolder.Direction ==1:
                        #        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYPeaks[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXPeaks[VarHolder.Direction])))

                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction] = list(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[self.VarHolder.Direction])
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[self.VarHolder.Direction] = list(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[self.VarHolder.Direction])
                        
                        plt.clf()
                        plt.title(self.VarHolder.CurrentROI) 
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
                        
                        Vmin = self.VarHolder.CurrentLevel - self.VarHolder.CurrentWidth
                        Vmax = self.VarHolder.CurrentLevel + self.VarHolder.CurrentWidth
                        self.plot(Vmin=Vmin,Vmax=Vmax)

                        self.VarHolder.Canvas.draw()
                        DonePeaks=True

                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction]) >0:
                    if DistancesTrough[IndexOfClosestTrough] < 0.1 and DonePeaks==False:
                        del self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction][IndexOfClosestTrough]
                        del self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[self.VarHolder.Direction][IndexOfClosestTrough]
                        
                        #if len(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction]) >0:
                        #    if VarHolder.Direction==0:
                        #        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction])))
                        #    elif VarHolder.Direction ==1:
                        #        VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction] = zip(*sorted(zip(VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsYTroughs[VarHolder.Direction], VarHolder.ManualResData[VarHolder.CurrentROI].ChosenPointsXTroughs[VarHolder.Direction])))

                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction] = list(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[self.VarHolder.Direction])
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[self.VarHolder.Direction] = list(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[self.VarHolder.Direction])
                        
                        plt.clf()
                        plt.title(self.VarHolder.CurrentROI) 
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
                        plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
                        
                        Vmin = self.VarHolder.CurrentLevel - self.VarHolder.CurrentWidth
                        Vmax = self.VarHolder.CurrentLevel + self.VarHolder.CurrentWidth
                        self.plot(Vmin=Vmin,Vmax=Vmax)
                        self.VarHolder.Canvas.draw()

    def DetectShiftPress(self,event):
        if event.key == 'shift':
            self.VarHolder.ShiftPressed = True
        if event.key == "control" :
            self.VarHolder.Direction = 1
            self.VarHolder.WinDirectionLabel.config(text = "Current Direction: Vertical")
        if event.key == "ctrl+shift" or event.key == "shift+control":
            self.VarHolder.ShiftPressed = True
            self.VarHolder.Direction = 1
            self.VarHolder.WinDirectionLabel.config(text = "Current Direction: Vertical")

    def DetectShiftReleased(self,event):
        if event.key == 'shift':
            self.VarHolder.ShiftPressed = False
        if event.key == "control":
            self.VarHolder.Direction = 0
            self.VarHolder.WinDirectionLabel.config(text = "Current Direction: Horizontal")
        if event.key == "ctrl+shift" or event.key == "shift+control":
            self.VarHolder.ShiftPressed = False
            self.VarHolder.Direction = 0
            self.VarHolder.WinDirectionLabel.config(text = "Current Direction: Horizontal")

        if event.key == "alt":
            print("Automatically fitting troughs..")
            for Direction in range(2):
                if len(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[Direction]) == 4:
                    if Direction==0:
                        SortedXPeaks, SortedYPeaks = zip(*sorted(zip(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[Direction], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[Direction])))
                    else:
                        SortedYPeaks, SortedXPeaks = zip(*sorted(zip(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[Direction], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[Direction])))

                    self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[Direction] = []
                    self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[Direction] = []

                    for idx in range(3):
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[Direction].append( (SortedXPeaks[idx] + SortedXPeaks[idx+1])/2.0 )
                        self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[Direction].append( (SortedYPeaks[idx] + SortedYPeaks[idx+1])/2.0 )

            plt.clf()
            plt.title(self.VarHolder.CurrentROI) 
            plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[0], marker="x",color="blue", linestyle = '')
            plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXPeaks[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYPeaks[1], marker="x",color="red", linestyle = '')
            plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[0], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[0], marker="o",color="blue", linestyle = '')
            plt.plot(self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsXTroughs[1], self.VarHolder.ManualResData[self.VarHolder.CurrentROI].ChosenPointsYTroughs[1], marker="o",color="red", linestyle = '')
            
            Vmin = self.VarHolder.CurrentLevel - self.VarHolder.CurrentWidth
            Vmax = self.VarHolder.CurrentLevel + self.VarHolder.CurrentWidth
            self.plot(Vmin=Vmin,Vmax=Vmax)
            self.VarHolder.Canvas.draw()