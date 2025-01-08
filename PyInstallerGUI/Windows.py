import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW
import pydicom
from pydicom.filereader import read_dicomdir
from pydicom import dcmread
import glob
import os 

def OverrideCentreAndRadiusWindow(root,dicomPath,seq):
    Win = tkinter.Toplevel(root)
    Win.iconbitmap("_internal\ct-scan.ico")
    Win.geometry("500x540")
    Win.configure(background='white')
    Win.resizable(False,False)
    plt.title("Select Centre of the Phantom")

    files = glob.glob(os.path.join(dicomPath,"*"))
    Dcms = []
    for file in files: 
        dicom = dcmread(file)
        if dicom.SeriesDescription == seq:
            Dcms.append(dicom)
    Dcms = sorted(Dcms, key=lambda d: d.SliceLocation)
    Image = Dcms[6].pixel_array
    plt.imshow(Image)
    canvas = FigureCanvasTkAgg(plt.gcf(), master = Win) 
    canvas.draw() 
    canvas.get_tk_widget().pack(side=TOP)
    toolbar = NavigationToolbar2Tk(canvas, Win) 
    toolbar.update() 
    canvas.get_tk_widget().pack() 

    root.wait_window(Win)