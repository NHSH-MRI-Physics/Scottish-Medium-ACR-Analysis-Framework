import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import StandardConfirmation
from tkinter import messagebox
import pickle
import sys
sys.path.append(".")
root = TkinterDnD.Tk()
root.title("Database Checker and Adder")
root.geometry("600x400")  # Width x Height
# Label placed at the top-left corner
label = tk.Label(
    root,
    text="Drag and drop a file here",
    width=40,
    height=5,
    bg="lightgray",
    anchor="center",        # Align text to the left inside the label
    justify="center",    # Align multiline text to the left
    font=("Arial", 12)
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

columns = ("Paramater","Standard", "DICOM", "Match?")
tree = ttk.Treeview(root, columns=columns, show="headings",height=14)

style = ttk.Style()
style.configure("Treeview.Heading", foreground="red", font=("Arial", 10, "bold"))

for col in columns:
    tree.heading(col, text=col)
tree.column("Paramater", width=50)
tree.column("Standard", width=50)
tree.column("DICOM", width=50)
tree.column("Match?", width=50)
for row in range(10):
    tree.insert("", tk.END, values=str(row))

tree.grid(padx=10, pady=10,row=1, column=0,sticky="sw")

def drop(event):
    files = root.tk.splitlist(event.data)
    if len(files) == 1:
        with open(files[0], 'rb') as f:
            data = pickle.load(f)
            result,data = StandardConfirmation.CheckAgainstStandard(data)
            if result == True:
                StandardLabel.config(bg="green",text="File meets the standard: \N{Check Mark}")
            else:
                StandardLabel.config(bg="red",text="File doesn't meet the standard: \N{Box Drawings Light Diagonal Cross}")
    else:
        messagebox.showwarning("Warning", "You dropped More Than One File!")
    
# Bind the drop event to the label
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

root.mainloop()