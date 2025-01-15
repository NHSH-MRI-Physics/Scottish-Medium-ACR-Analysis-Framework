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
            if len(self.points) < 4:
                self.points.append((event.xdata, event.ydata))

            plt.clf()
            plt.imshow(self.Image)
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
                plt.imshow(self.Image)
                plt.title(self.Title)
                if self.PreCalcdCentre != None:
                    plt.plot(self.PreCalcdCentre[0],self.PreCalcdCentre[1],marker="x",color="red")
                for point in self.points:
                    plt.plot(point[0],point[1],'ro')    
                self.canvas.draw()         
            

    def Reset(self):
        plt.clf()
        plt.imshow(self.Image)
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
        plt.imshow(self.Image)
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