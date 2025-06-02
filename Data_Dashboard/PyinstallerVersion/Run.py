import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sv_ttk
from tkinter import StringVar
import FileAnalysis

class BoardData(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IndividualData(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


root = tk.Tk()
sv_ttk.set_theme("dark")
root.geometry('1200x500')


#Load file component
file_frame = tk.Frame(root)
file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
LoadedFileVar = StringVar()
LoadedFileVar.set("Not Set!")
LoadedFilePath = ttk.Label(master=root,textvariable=LoadedFileVar)

FileData = None

def load_file():
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(("Text Files", "*.xlsx"), ("All Files", "*.*"))
    )
    if file_path:
        LoadedFileVar.set(file_path)
        FileData = FileAnalysis.LoadedData(file_path)

load_button = ttk.Button(file_frame, text="Load and Analyse File", command=load_file)
load_button.grid(row=0, column=0,sticky="NW")
LoadedFilePath.grid(row=0, column=1,padx=10,pady=2,sticky="W")


notebook = ttk.Notebook()
BoardDataObj = BoardData(notebook)
notebook.add(BoardDataObj, text="Board Data", padding=10)
IndividualDataObj = IndividualData(notebook)
notebook.add(IndividualDataObj, text="Individual Data", padding=10)
notebook.grid(row=1, column=0, padx=10, pady=10,columnspan=2, sticky="nsew")
root.grid_rowconfigure(1, weight=1)  # Allow row 1 (notebook) to expand
root.grid_columnconfigure(1, weight=1)
root.mainloop()