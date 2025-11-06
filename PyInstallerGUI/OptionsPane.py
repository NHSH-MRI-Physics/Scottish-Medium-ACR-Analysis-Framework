from tkinter import ttk
from tkinter import StringVar, IntVar
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW

from MedACROptions import GeometryOptions,UniformityOptions, ResOptions

#This is for the UI
class OptionsPaneHolder():
    def __init__(self):
        self.SpatialResOption=StringVar()
        #self.SpatialResOption.set("Manual")
        self.SpatialResOption.set("Contrast Response")
        self.GeoAccOption=StringVar()
        self.GeoAccOption.set("MagNet Method")
        self.UniformityOption=StringVar()
        self.UniformityOption.set("ACR Method")

        self.OverrideRadiusAndCentre = IntVar(value=0)
        self.OverrideMasking = IntVar(value=0)
        self.OverideResBlockLoc=IntVar(value=0)
        self.UseLegacySliceThicknessAlgo=IntVar(value=0)
        self.DumpToExcel=IntVar(value=0)
        self.FixedManualROISize=IntVar(value=1)
        self.LoadPreviousRun=IntVar(value=0)

        self.Use11mm=IntVar(value=1)
        self.Use10mm=IntVar(value=1)
        self.Use09mm=IntVar(value=0)
        self.Use08mm=IntVar(value=0)
        
        self.currentRow = 0
        self.OptionsPane = None

    def AddOptionRowDropdown(self,options,variable,label):
        label = ttk.Label(self.OptionsPane, text=label, anchor='w')
        #options = [self.SpatialResOption.get(),"Contrast Response", "MTF", "Dot Matrix", "Manual", ] 
        drop = ttk.OptionMenu( self.OptionsPane , variable , *options) 
        drop.config(width = 20)
        label.grid(row=self.currentRow, column=0,padx=5,sticky=W)
        drop.grid(row=self.currentRow, column=0,padx=135,sticky=W)
        self.currentRow+=1

    def AddOptionRowCheckbox(self,text,variable,padding=5):
        CheckBox = ttk.Checkbutton(self.OptionsPane, text=text,variable=variable, onvalue=1, offvalue=0,state=NORMAL)
        CheckBox.grid(row=self.currentRow, column=0,padx=padding,sticky=W,columnspan=2)
        self.currentRow+=1

    def AddButton(self,text,command):
        button = ttk.Button(self.OptionsPane, text=text, command=command)
        button.grid(row=self.currentRow, column=0,padx=5,sticky=W,columnspan=2)
        self.currentRow+=1

    def SetupOptions(self,OptionsPane):       
        self.OptionsPane = OptionsPane

        self.AddOptionRowDropdown([ self.SpatialResOption.get(),"Contrast Response", "MTF", "Dot Matrix", "Manual", ],self.SpatialResOption,"Spatial Res Method")
        self.AddOptionRowDropdown([ self.GeoAccOption.get() , "MagNet Method", "ACR Method",],self.GeoAccOption,"Geo Acc Method")
        self.AddOptionRowDropdown([ self.UniformityOption.get(), "ACR Method" , "MagNet Method",],self.UniformityOption,"Uniformity Method")

        self.AddOptionRowCheckbox(text='Override Radius and Centre',variable=self.OverrideRadiusAndCentre)
        self.AddOptionRowCheckbox(text='Override Masking',variable=self.OverrideMasking)
        self.AddOptionRowCheckbox(text='Override Res Blocks Location',variable=self.OverideResBlockLoc)
        self.AddOptionRowCheckbox(text='Use Legacy Slice Thickness Bar Algorithm',variable=self.UseLegacySliceThicknessAlgo)
        self.AddOptionRowCheckbox(text='Dump Results to Excel file',variable=self.DumpToExcel)
        self.AddOptionRowCheckbox(text='Fixed manual ROI size',variable=self.FixedManualROISize)
        self.AddOptionRowCheckbox(text="Load in Previous Run", variable=self.LoadPreviousRun)

        labelRes = ttk.Label(self.OptionsPane, text="Manual Res Targets", anchor='s')
        labelRes.grid(row=self.currentRow, column=0,padx=5,pady=5,sticky=W+S)
        self.currentRow+=1
        self.AddOptionRowCheckbox(text="1.1mm", variable=self.Use11mm,padding=15)
        self.AddOptionRowCheckbox(text="1.0mm", variable=self.Use10mm,padding=15)
        self.AddOptionRowCheckbox(text="0.9mm", variable=self.Use09mm,padding=15)
        self.AddOptionRowCheckbox(text="0.8mm", variable=self.Use08mm,padding=15)

        self.OptionsPane.grid_columnconfigure(0, weight=1)
        self.OptionsPane.grid_rowconfigure(0, weight=1)

    def GetOptions(self):
        OptionsDict = {}
        OptionsDict["GeoAccOption"] = self.GeoAccOption.get()
        OptionsDict["SpatialResOption"] = self.SpatialResOption.get()
        OptionsDict["OverrideRadiusAndCentre"] = self.OverrideRadiusAndCentre.get()
        OptionsDict["OverrideMasking"] = self.OverrideMasking.get()
        OptionsDict["OverideResBlockLoc"] = self.OverideResBlockLoc.get()
        OptionsDict["UseLegacySliceThicknessAlgo"] = self.UseLegacySliceThicknessAlgo.get()
        OptionsDict["DumpToExcel"] = self.DumpToExcel.get()
        OptionsDict["UniformityOptions"] = self.UniformityOption.get()
        OptionsDict["FixedManualROISize"] = self.FixedManualROISize.get()
        OptionsDict["LoadPreviousRun"] = self.LoadPreviousRun.get()
        OptionsDict["Use11mm"] = self.Use11mm.get()
        OptionsDict["Use10mm"] = self.Use10mm.get()
        OptionsDict["Use09mm"] = self.Use09mm.get()
        OptionsDict["Use08mm"] = self.Use08mm.get()

        return OptionsDict
    
    def SetOptions(self,OptionsDict):
        self.GeoAccOption.set(OptionsDict["GeoAccOption"])
        self.SpatialResOption.set(OptionsDict["SpatialResOption"])
        self.OverrideRadiusAndCentre.set(OptionsDict["OverrideRadiusAndCentre"])
        self.OverrideMasking.set(OptionsDict["OverrideMasking"])
        self.OverideResBlockLoc.set(OptionsDict["OverideResBlockLoc"])
        self.UseLegacySliceThicknessAlgo.set(OptionsDict["UseLegacySliceThicknessAlgo"])
        self.DumpToExcel.set(OptionsDict["DumpToExcel"])
        self.UniformityOption.set(OptionsDict["UniformityOptions"])
        self.FixedManualROISize.set(OptionsDict["FixedManualROISize"])
        self.LoadPreviousRun.set(OptionsDict["LoadPreviousRun"])

        if "Use11mm" in OptionsDict:
            self.Use11mm.set(OptionsDict["Use11mm"])
        else:
            self.Use11mm.set(1)

        if "Use10mm" in OptionsDict:
            self.Use10mm.set(OptionsDict["Use10mm"])
        else:
            self.Use10mm.set(1)

        if "Use09mm" in OptionsDict:
            self.Use09mm.set(OptionsDict["Use09mm"])
        else:
            self.Use09mm.set(0)

        if "Use08mm" in OptionsDict:
            self.Use08mm.set(OptionsDict["Use08mm"])
        else:
            self.Use08mm.set(0)
