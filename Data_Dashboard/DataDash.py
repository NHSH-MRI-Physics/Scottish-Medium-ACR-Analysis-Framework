import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import glob
import pickle
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MedACRModules.Empty_Module import EmptyModule
from MedACRModules.SNR_Module import SNRModule
from MedACRModules.Geo_Acc_Module import GeoAccModule
from MedACRModules.Uniformity_Module import UniformityModule
from MedACRModules.SlicePos_Module import SlicePosModule
from MedACRModules.Ghosting_Module import GhostingModule
from MedACRModules.SliceThickness_Module import SliceThicknessModule
from MedACRModules.Spatial_res_Module import SpatialResModule

st.set_page_config(
    page_title="Data Dashboard Home",
    page_icon="📊"
)

st.title("Med ACR Data Dashboard")
database_path = "Result_Database"
pkl_files = glob.glob(os.path.join(database_path, "*.pkl"))


Results = {}
scanner_rows = []
for file in pkl_files:
    Data = pickle.load(open(file,'rb'))
    for key in Data:
        if key != "date" or key != "ScannerDetails":
            if key not in Results:
                Results[key] = []
            Results[key].append([Data[key],Data["date"],Data["ScannerDetails"]])
        
        row = {
            "Manufacturer": str(Data["ScannerDetails"].get("Manufacturer", "")),
            "Institution Name": str(Data["ScannerDetails"].get("Institution Name", "")),
            "Model Name": str(Data["ScannerDetails"].get("Model Name", "")),
            "Serial Number": str(Data["ScannerDetails"].get("Serial Number", "")),
        }
        scanner_rows.append(row)

df = pd.DataFrame(scanner_rows)
df = df.drop_duplicates() 

def dataframe_with_selections(df: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)

st.subheader("Dataset selection")
SelectedData = dataframe_with_selections(df)

def FilerData(Selection,TestName):
    DataToKeep = []
    for i in range(len(Selection)):
        for result in Results[TestName]:#This bit is broken for the second of two results files
            if result[2]["Manufacturer"] == Selection["Manufacturer"][i] and result[2]["Institution Name"] == Selection["Institution Name"][i] and result[2]["Model Name"] == Selection["Model Name"][i] and result[2]["Serial Number"] == Selection["Serial Number"][i]:
                DataToKeep.append(result)
    return DataToKeep   

st.divider()
st.subheader("Signal to Noise Ratio")

FilteredResults = FilerData(SelectedData,"SNR")
print("--------")
if FilteredResults != None:
    for Result in FilteredResults:
        print(Result)