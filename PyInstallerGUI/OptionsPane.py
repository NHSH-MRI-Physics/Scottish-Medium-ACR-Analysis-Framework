from tkinter import ttk
from tkinter import StringVar, IntVar
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW

#This is for the UI

SpatialResOption=StringVar()
SpatialResOption.set("Manual")
SpatialResOption.set("Contrast Response")
GeoAccOption=StringVar()
GeoAccOption.set("MagNet Method")

OverrideRadiusAndCentre = IntVar(value=0)
OverrideMasking = IntVar(value=0)
OverideResBlockLoc=IntVar(value=0)
UseLegacySliceThicknessAlgo=IntVar(value=0)
DumpToExcel=IntVar(value=1)

def SetupOptions(OptionsPane):
    #Im sure this can be done better but i think al leave it for now
    global SpatialResOption
    global GeoAccOption
    global OverrideRadiusAndCentre
    global UseLegacySliceThicknessAlgo
    global DumpToExcel

    label = ttk.Label(OptionsPane, text="Spatial Res Method", anchor='w')

    options = [SpatialResOption.get(),"Contrast Response", "MTF", "Dot Matrix", "Manual", ] 
    drop = ttk.OptionMenu( OptionsPane , SpatialResOption , *options ) 
    drop.config(width = 20)
    label.grid(row=0, column=0,padx=5,sticky=W)
    drop.grid(row=0, column=1,padx=5,sticky=W)

    label = ttk.Label(OptionsPane, text="Geo Acc Method", anchor='w')
    options = [ GeoAccOption.get() , "MagNet Method", "ACR Method",] 
    drop = ttk.OptionMenu( OptionsPane , GeoAccOption , *options ) 
    drop.config(width = 13)
    drop.grid(row=1, column=1,padx=5,sticky=W)
    label.grid(row=1, column=0,padx=5,sticky=W)


    CheckBox = ttk.Checkbutton(OptionsPane, text='Override Radius and Centre',variable=OverrideRadiusAndCentre, onvalue=1, offvalue=0,state=NORMAL)
    CheckBox.grid(row=2, column=0,padx=5,sticky=W,columnspan=2)

    CheckBox = ttk.Checkbutton(OptionsPane, text='Override Masking',variable=OverrideMasking, onvalue=1, offvalue=0,state=NORMAL)
    CheckBox.grid(row=3, column=0,padx=5,sticky=W,columnspan=2)

    CheckBox = ttk.Checkbutton(OptionsPane, text='Override Res Blocks Location',variable=OverideResBlockLoc, onvalue=1, offvalue=0,state=NORMAL)
    CheckBox.grid(row=4, column=0,padx=5,sticky=W,columnspan=2)

    CheckBox = ttk.Checkbutton(OptionsPane, text='Use Legacy Slice Thickness Bar Algorithm',variable=UseLegacySliceThicknessAlgo, onvalue=1, offvalue=0,state=NORMAL)
    CheckBox.grid(row=5, column=0,padx=5,sticky=W,columnspan=2)

    CheckBox = ttk.Checkbutton(OptionsPane, text='Dump Results to Excel file',variable=DumpToExcel, onvalue=1, offvalue=0,state=NORMAL)
    CheckBox.grid(row=6, column=0,padx=5,sticky=W,columnspan=2)

def GetOptions():
    #global SpatialResOption
    #global GeoAccOption
    OptionsDict = {}
    OptionsDict["GeoAccOption"] = GeoAccOption.get()
    OptionsDict["SpatialResOption"] = SpatialResOption.get()
    OptionsDict["OverrideRadiusAndCentre"] = OverrideRadiusAndCentre.get()
    OptionsDict["OverrideMasking"] = OverrideMasking.get()
    OptionsDict["OverideResBlockLoc"] = OverideResBlockLoc.get()
    OptionsDict["UseLegacySliceThicknessAlgo"] = UseLegacySliceThicknessAlgo.get()
    OptionsDict["DumpToExcel"] = DumpToExcel.get()

    return OptionsDict