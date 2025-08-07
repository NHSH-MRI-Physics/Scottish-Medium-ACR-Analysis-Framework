import streamlit as st
import plotly.express as px
def GetDataAndPlot(df_FullData,UniqueIDS):
    filtered_df = df_FullData[df_FullData["ScannerUniqueID"].isin(UniqueIDS)]
    filtered_df["SNR"] = [None]*len(filtered_df)

    for idx, row in filtered_df.iterrows():
        data = row["Tests"]  
        filtered_df.at[idx, "SNR"] = data["SNR"].results["measurement"]["snr by smoothing"]["measured"]
        filtered_df.at[idx, "ScannerUniqueID"] = filtered_df.at[idx, "ScannerUniqueID"] + " " + filtered_df.at[idx, "Sequence"]
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
    
    return fig