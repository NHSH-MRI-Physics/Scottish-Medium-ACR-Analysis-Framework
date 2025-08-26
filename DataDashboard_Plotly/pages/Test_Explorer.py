import dash
from dash import Dash, dcc, html, Input, Output, callback
from plotly_calplot import calplot
import pandas as pd
import numpy as np
from dash import dash_table
import sys
import GetData
import datetime
import plotly.graph_objects as go
import plotly.express as px
from skimage.transform import resize
dash.register_page(__name__,name='Test Explorer')

#Make some dummy date
#full_df = GetData.GetDummyData()    
full_df = GetData.loadDatabase("TestDBForDashBoard")
Tabledf = full_df.iloc[0:0]

#Get years in the date
years = full_df['Date'].dt.year.unique()
Dropdown =  dcc.Dropdown(
        id='Date-Dropdown',
        options=years,
        value=years[0],
        clearable=False,
        style={'width': '300px'}
    )
filtered_df = full_df[full_df['Date'].dt.year == years[0]]

#Make a plot to start with using the first year
fig = calplot(
    filtered_df,
    x="Date",
    y="TestCount",
    years_title=True,
    dark_theme=True
)

layout = html.Div([
    html.H1('Test Explorer'),
    html.Div('Choose a year.'),
    Dropdown,
    dcc.Graph(figure=fig,id="Date-Plot"),
    html.Br(),
    html.Div(id="table",style={'display': 'flex', 'justifyContent': 'center'}),
    html.Br(),
    html.Div(id='DisplayTest',style={'display': 'flex', 'justifyContent': 'center'})
])


@dash.callback(
    Output('Date-Plot', 'figure'),
    Input('Date-Dropdown', 'value')
)
def update_figure(selected):
    filtered_df = full_df[full_df['Date'].dt.year == selected]
    fig = calplot(
    filtered_df,
    x="Date",
    y="TestCount",
    years_title=True,
    dark_theme=True
    )
    return fig


@dash.callback(
    Output('table', 'children'),
    Input('Date-Plot', 'clickData'),
    Input('Date-Dropdown', 'value')
)
def display_click(clickData, selected_year):
    filtered_df = full_df[full_df['Date'].dt.year == selected_year]
    if clickData is not None:
        date = clickData['points'][0]['customdata'][0]
        DataForDate = filtered_df[filtered_df["Date"] == pd.to_datetime(date)]
        TableData = pd.DataFrame()
        Date= []
        Tests = []
        ScannerModel = []
        ScannerSerialNumber = []
        InstitutionName = []
        ScannerSerialNumber=[]
        ScannerManufacuter=[]
        Times = []
        Sequence = []
        ProcessTimeDate = []

        for i in range(DataForDate["TestCount"].values[0]):
            Date.append(DataForDate["Date"].values[0])
            ScannerModel.append(DataForDate["ScannerModel"].values[0][i])
            Tests.append(DataForDate["Tests"].values[0][i])
            Times.append(DataForDate["Time"].values[0][i])
            ScannerSerialNumber.append(DataForDate["ScannerSerialNumber"].values[0][i])
            InstitutionName.append(DataForDate["InstitutionName"].values[0][i])
            ScannerManufacuter.append(DataForDate["ScannerManufacuter"].values[0][i])
            Sequence.append(DataForDate["Sequence"].values[0][i])
            ProcessTimeDate.append(DataForDate["ProcessTimeDate"].values[0][i])

        if DataForDate["TestCount"].values[0] >0:
            TableData["Date"] = Date
            TableData["Date"] = TableData["Date"].dt.strftime("%Y-%m-%d")
            TableData["ScannerModel"] = ScannerModel
            TableData["InstitutionName"] = InstitutionName
            TableData["ScannerManufacuter"] = ScannerManufacuter
            TableData["ScannerSerialNumber"] = ScannerSerialNumber
            TableData["Sequence"] = Sequence
            TableData["Time"] = Times
            
            TableData["ProcessTimeDate"] = ProcessTimeDate
            TableData["ProcessTimeDate"] = TableData["ProcessTimeDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            TableData = filtered_df.iloc[0:0] 

    else:
        TableData = filtered_df.iloc[0:0]  # Empty table
    return dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": "Scan Date", "id": "Date", "deletable": False, "selectable": True},
            {"name": "Scan Time", "id": "Time", "deletable": False, "selectable": True},
            {"name": "Sequence", "id": "Sequence", "deletable": False, "selectable": True},
            {"name": "Scanner Manufacuter", "id": "ScannerManufacuter", "deletable": False, "selectable": True},
            {"name": "Scanner Model", "id": "ScannerModel", "deletable": False, "selectable": True},
            {"name": "Institution Name", "id": "InstitutionName", "deletable": False, "selectable": True},
            {"name": "Scanner Serial Number", "id": "ScannerSerialNumber", "deletable": False, "selectable": True},
            {"name": "Analysis Date and Time", "id": "ProcessTimeDate", "deletable": False, "selectable": True}
        ],
        data=TableData.to_dict('records'),
        editable=False,
        #sort_action="native",
        #sort_mode="multi",
        row_selectable="single",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_header={
            'backgroundColor': '#222',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_cell={
            'backgroundColor': '#333',
            'color': 'white',
            'border': '1px solid #444',
            'minWidth': '100px',
            'textAlign': 'center'
        },
        style_data={
            'backgroundColor': '#333',
            'color': 'white'
        },
        style_table={'width': '20%'}
    )

@callback(
    Output('DisplayTest', 'children'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_output(derived_virtual_data, derived_virtual_selected_rows):
    if derived_virtual_selected_rows:
        selected_row = derived_virtual_data[derived_virtual_selected_rows[0]]
        DataForDate = filtered_df[filtered_df["Date"] == pd.to_datetime(selected_row["Date"])]
        
        #This makes sure it all in the same format
        selected_row["Time"] = datetime.datetime.strptime(selected_row["Time"],"%H:%M:%S").time()
        selected_row["ProcessTimeDate"] = datetime.datetime.strptime(selected_row["ProcessTimeDate"],"%Y-%m-%d %H:%M:%S")

        ChosenData=None
        for i in range(DataForDate["TestCount"].values[0]):
            CorrectElements = 0

            for key in selected_row.keys():
                if key == "Date":
                    continue
                if DataForDate[key].values[0][i] == selected_row[key]:
                    CorrectElements+=1
            
            if CorrectElements == len(selected_row.keys())-1:
                ChosenData = {}
                for key in selected_row.keys():
                    if (type(DataForDate[key].values[0])) == list:
                        ChosenData[key] = DataForDate[key].values[0][i]
                    else:        
                        ChosenData[key] = DataForDate[key].values[0]
                ChosenData["Date"] = pd.to_datetime(ChosenData["Date"])
                ChosenData["ProcessTimeDate"] = pd.to_datetime(ChosenData["ProcessTimeDate"])
                ChosenData["TestData"] = DataForDate["Tests"].values[0][i]


        TestAndScannerDetailsTable = html.Table(
            [
            html.Caption("Test and Scanner Details",style={"caption-side":"top"}),
            html.Tr(
                [
                    html.Th("Test Date and Time",style={'border':'2px solid #444',"width":"15%",'textAlign': 'center'}),
                    html.Th(ChosenData["Date"].strftime("%d-%m-%Y") + " " + ChosenData["Time"].strftime("%H-%M-%S"),style={'textAlign': 'center','border':'2px solid #444',"width":"15%"})
                ]),
            html.Tr(
                [
                    html.Th("Sequence",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["Sequence"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            html.Tr(
                [
                    html.Th("Scanner Manufacuter",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["ScannerManufacuter"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            html.Tr(
                [
                    html.Th("Scanner Model",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["ScannerModel"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            html.Tr(
                [
                    html.Th("Institution Name",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["InstitutionName"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            html.Tr(
                [
                    html.Th("Scanner Serial Number",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["ScannerSerialNumber"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            html.Tr(
                [
                    html.Th("Analysis Date and Time",style={'border':'2px solid #444','textAlign': 'center'}),
                    html.Th(ChosenData["ProcessTimeDate"],style={'textAlign': 'center','border':'2px solid #444'})
                ]),
            ],
            style={'backgroundColor': '#333',
                   'width':'100%'},
            title="Scanner and Test Details"
        )

        DCMImages = []
        for i in range(len(ChosenData['TestData']['DICOM'])):
            Image = resize(ChosenData['TestData']['DICOM'][i].pixel_array, (400,400), order=3)
            DCMImages.append(Image)
        fig = GetDICOMFigure(DCMImages,0)

        DICOMView = html.Div([
                            dcc.Graph(id="plot",figure=fig,responsive=False),
                            html.Div([html.Button("<-"),html.Button("->")],style={'display': 'flex', 'justifyContent': 'center'})
                            ])
            
        HTMLComponents = html.Table(
            html.Tr(
                [
                html.Th(TestAndScannerDetailsTable,style={"width":"40%",'border':'2px solid #444'}),
                html.Th(DICOMView)
                ] 
            ),
            style={'backgroundColor': '#333',
                   'width':'60%'},
            )

        #TODO Justify the image centreally
        #TODO figure out how to make the div or table smaller in the height direction

        return HTMLComponents
                                

def GetDICOMFigure(DCMImages,Index):
        fig = px.imshow(DCMImages[Index],color_continuous_scale = 'gray')
        fig.update_layout({
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        })
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

        return fig