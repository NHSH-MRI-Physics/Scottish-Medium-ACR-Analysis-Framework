import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import StandardConfirmation
from tkinter import messagebox
import pickle
import sys
import os
import gspread

sys.path.append(".")
root = TkinterDnD.Tk()
root.title("Database Checker and Adder")
root.geometry("800x400")  # Width x Height
resultDict = None
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
FileDropped.grid(padx=10, pady=10,row=1, column=1)

def Update_Spreadsheet():
    try:
        gc = gspread.service_account(filename="DatabaseWriter/qaproject-441416-f5fec0c61099.json")
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1pbH3O7yJwCc05Ktlb643T3rXZsN-EqXcTJfmnz37FU0/edit?gid=0#gid=0")
        values_list = sh.worksheet("Data").col_values(1)
        LastRow = len(values_list)+1
        #sh.worksheet("Data").update( [[1,2,3,4]],"A"+str(LastRow))

        FileDropped.config(text="No File Dropped")
        StandardLabel.config(bg="lightgray",text="No File Dropped")
        messagebox.showinfo(title="Success",message="Spreadsheet updated!")

    except Exception as e:
        messagebox.showerror("Exception raised",message = str(repr(e)))


UpdateSpread = tk.Button(root, text="Update Spreadsheet", command=Update_Spreadsheet)
UpdateSpread.grid(padx=10, pady=10,row=2, column=1)
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

tree.grid(padx=10, pady=10,row=1, column=0,sticky="sw",rowspan=2)

def drop(event):
    files = root.tk.splitlist(event.data)
    UpdateSpread.config(state="disabled")
    if len(files) == 1:
        with open(files[0], 'rb') as f:
            data = pickle.load(f)
            result,resultDict = StandardConfirmation.CheckAgainstStandard(data)
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
    
# Bind the drop event to the label
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

root.mainloop()