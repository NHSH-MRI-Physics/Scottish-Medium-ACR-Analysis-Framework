from tkinter import ttk
from tkinter import StringVar, IntVar
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW

SpatialResOption=StringVar()
SpatialResOption.set("Contrast Response")
GeoAccOption=StringVar()
GeoAccOption.set("MagNet Method")

OverrideRadiusAndCentre = IntVar(value=0)
OverrideMasking = IntVar(value=0)

def SetupOptions(OptionsPane):
    #Im sure this can be done better but i think al leave it for now
    global SpatialResOption
    global GeoAccOption
    global OverrideRadiusAndCentre

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


def GetOptions():
    global SpatialResOption
    global GeoAccOption
    OptionsDict = {}
    OptionsDict["GeoAccOption"] = GeoAccOption.get()
    OptionsDict["SpatialResOption"] = SpatialResOption.get()
    OptionsDict["OverrideRadiusAndCentre"] = OverrideRadiusAndCentre.get()
    OptionsDict["OverrideMasking"] = OverrideMasking.get()

    return OptionsDict