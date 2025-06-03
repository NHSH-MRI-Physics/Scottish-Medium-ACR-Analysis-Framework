import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import glob
import pickle
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from MedACRModules.Empty_Module import EmptyModule
from MedACRModules.SNR_Module import SNRModule
from MedACRModules.Geo_Acc_Module import GeoAccModule
from MedACRModules.Uniformity_Module import UniformityModule
from MedACRModules.SlicePos_Module import SlicePosModule
from MedACRModules.Ghosting_Module import GhostingModule
from MedACRModules.SliceThickness_Module import SliceThicknessModule
from MedACRModules.Spatial_res_Module import SpatialResModule

import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Data Dashboard Home",
    page_icon="📊"
)

st.title("Med ACR Data Dashboard")
database_path = "Result_Database"
pkl_files = glob.glob(os.path.join(database_path, "*.pkl"))


#Results = {}
scanner_rows = []
for file in pkl_files:
    Data = pickle.load(open(file,'rb'))
    row = {
        "Manufacturer": str(Data["ScannerDetails"].get("Manufacturer", "")),
        "Institution Name": str(Data["ScannerDetails"].get("Institution Name", "")),
        "Model Name": str(Data["ScannerDetails"].get("Model Name", "")),
        "Serial Number": str(Data["ScannerDetails"].get("Serial Number", "")),
        "FileName": file,
        "date": Data["date"],
        "ScannerUniqueID": str(Data["ScannerDetails"].get("Manufacturer", ""))+"_"+str(Data["ScannerDetails"].get("Institution Name", ""))+"_"+str(Data["ScannerDetails"].get("Model Name", ""))+"_"+str(Data["ScannerDetails"].get("Serial Number", "")),
        "Data": Data
    }
    scanner_rows.append(row)

df_DisplayData = pd.DataFrame(scanner_rows,dtype=object).drop("FileName",axis=1).drop("date",axis=1).drop("ScannerUniqueID",axis=1).drop("Data",axis=1)
df_DisplayData = df_DisplayData.drop_duplicates() 
df_FullData = pd.DataFrame(scanner_rows)

def dataframe_with_selections(df: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)

st.subheader("Dataset selection")
SelectedData = dataframe_with_selections(df_DisplayData)

#Remake UniqueIDs
manufacturers = list(SelectedData["Manufacturer"])
models = list(SelectedData["Model Name"])
InstitutionName = list(SelectedData["Institution Name"])
SerialNumber = list(SelectedData["Serial Number"])

UniqueIDS = []
for i in range(len(manufacturers)):
    UniqueIDS.append(manufacturers[i] + "_" + InstitutionName[i] + "_" + models[i] + "_" + SerialNumber[i])


filtered_df = df_FullData[df_FullData["ScannerUniqueID"].isin(UniqueIDS)]
filtered_df["SNR"] = [None]*len(filtered_df)

for idx, row in filtered_df.iterrows():
    data = row["Data"]  
    filtered_df.at[idx, "SNR"] = data["SNR"].results["measurement"]["snr by smoothing"]["measured"]


st.divider()
st.subheader("SNR")
fig = px.scatter(filtered_df, x="date", y="SNR",color="ScannerUniqueID")
fig.update_layout(
        title=dict(
        text="SNR Data",
        y=0.95,
        x=0.5,
        xanchor='center',
        yanchor='top'
    ),
    legend=dict(
        orientation="h",  # horizontal orientation
        yanchor="bottom",
        y=-0.5,  # position below plot
        xanchor="left",
        x=0,
        title=None
    )
)
st.plotly_chart(fig)