from tkinter import ttk
from tkinter import StringVar, IntVar
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW

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
        self.DumpToExcel=IntVar(value=1)
        self.FixedManualROISize=IntVar(value=1)
        
        self.currentRow = 0
        self.OptionsPane = None

    def AddOptionRowDropdown(self,options,variable,label):
        label = ttk.Label(self.OptionsPane, text=label, anchor='w')
        #options = [self.SpatialResOption.get(),"Contrast Response", "MTF", "Dot Matrix", "Manual", ] 
        drop = ttk.OptionMenu( self.OptionsPane , variable , *options ) 
        drop.config(width = 20)
        label.grid(row=self.currentRow, column=0,padx=5,sticky=W)
        drop.grid(row=self.currentRow, column=1,padx=5,sticky=W)
        self.currentRow+=1

    def AddOptionRowCheckbox(self,text,variable):
        CheckBox = ttk.Checkbutton(self.OptionsPane, text=text,variable=variable, onvalue=1, offvalue=0,state=NORMAL)
        CheckBox.grid(row=self.currentRow, column=0,padx=5,sticky=W,columnspan=2)
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

        return OptionsDict