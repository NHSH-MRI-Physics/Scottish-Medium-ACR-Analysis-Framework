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

class CentreRadiusMaskingWindow():
    def __init__(self,root,dicomPath,seq,overridemasking = False, slice=7,PreCalcdCentre = None):
        slice -=1 #Convert it back to index that starts at 0
        self.points = []
        self.Centrex = None
        self.Centrey = None
        self.Radius = None
        self.Mask = None
        self.PreCalcdCentre = PreCalcdCentre
        files = glob.glob(os.path.join(dicomPath,"*"))
        Dcms = []
        for file in files: 
            dicom = dcmread(file)
            if dicom.SeriesDescription == seq:
                Dcms.append(dicom)
        self.Dcms = sorted(Dcms, key=lambda d: d.SliceLocation)
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
        files = glob.glob(os.path.join(dicomPath,"*"))
        Dcms = []
        for file in files: 
            dicom = dcmread(file)
            if dicom.SeriesDescription == seq:
                Dcms.append(dicom)
        self.Dcms = sorted(Dcms, key=lambda d: d.SliceLocation)
        self.MakingRect = False
        self.Rect = [None,None,None,None]
        self.SelectedRects = [None,None,None,None]
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
        plt.gcf().canvas.callbacks.connect('button_press_event', self.on_click_on_plot)
        plt.gcf().canvas.callbacks.connect('button_release_event', self.release_click_on_plot)
        plt.gcf().canvas.callbacks.connect("motion_notify_event", self.onmove)
        
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
