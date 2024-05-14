import tkinter
from tkinter import ttk
import sv_ttk
from tkinter import filedialog
from tkinter import StringVar

root = tkinter.Tk()
root.geometry('1000x400')

def SetDCMPath():
    filename = filedialog.askdirectory()
    DCMfolder_path.set(filename)
def SetResultsOutput():
    filename = filedialog.askdirectory()
    Resultsfolder_path.set(filename)

PathFrame = ttk.Frame(root)
DCMPathButton = ttk.Button(text="Set DICOM Path", command=SetDCMPath,width=20)
DCMPathButton.grid(row=0, column=0)
DCMfolder_path = StringVar()
DCMfolder_path.set("Not Set!")
DCMPathLabel = ttk.Label(master=root,textvariable=DCMfolder_path)
DCMPathLabel.grid(row=0, column=1)

PathFrame = ttk.Frame(root)
ResultsPathButton = ttk.Button(text="Set Results Output Path", command=SetResultsOutput,width=20)
ResultsPathButton.grid(row=1, column=0)
Resultsfolder_path = StringVar()
Resultsfolder_path.set("Not Set!")
ResultsPathLabel = ttk.Label(master=root,textvariable=Resultsfolder_path)
ResultsPathLabel.grid(row=1, column=1)

sv_ttk.set_theme("dark")
root.mainloop()