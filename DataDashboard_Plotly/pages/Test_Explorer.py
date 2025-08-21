import dash
from dash import Dash, dcc, html, Input, Output, callback
from plotly_calplot import calplot
import pandas as pd
import numpy as np
from dash import dash_table
import sys
import GetData
dash.register_page(__name__,name='Test Explorer')

#Make some dummy date
full_df = GetData.GetDummyData()    
Tabledf = full_df.iloc[0:0]

#Get years in the date
years = full_df['date'].dt.year.unique()
Dropdown =  dcc.Dropdown(
        id='Date-Dropdown',
        options=years,
        value=years[0],
        clearable=False,
        style={'width': '300px'}
    )
filtered_df = full_df[full_df['date'].dt.year == years[0]]

#Make a plot to start with using the first year
fig = calplot(
    filtered_df,
    x="date",
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
    html.Div(id='hidden-div', style={'display':'none'})
])


@dash.callback(
    Output('Date-Plot', 'figure'),
    Input('Date-Dropdown', 'value')
)
def update_figure(selected):
    filtered_df = full_df[full_df['date'].dt.year == selected]
    fig = calplot(
    filtered_df,
    x="date",
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
    filtered_df = full_df[full_df['date'].dt.year == selected_year]
    if clickData is not None:
        date = clickData['points'][0]['customdata'][0]
        TableData = filtered_df[filtered_df["date"] == pd.to_datetime(date)]
        TableData["date"] = TableData["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        TableData = filtered_df.iloc[0:0]  # Empty table
    return dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": "date", "id": "date", "deletable": False, "selectable": True}
        ],
        data=TableData.to_dict('records'),
        editable=False,
        sort_action="native",
        sort_mode="multi",
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
            'fontWeight': 'bold'
        },
        style_cell={
            'backgroundColor': '#333',
            'color': 'white',
            'border': '1px solid #444',
            'minWidth': '100px'
        },
        style_data={
            'backgroundColor': '#333',
            'color': 'white'
        },
        style_table={'width': '20%'}
    )

@callback(
    Output('hidden-div', 'children'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_output(derived_virtual_data, derived_virtual_selected_rows):
    if derived_virtual_selected_rows:
        selected_row = derived_virtual_data[derived_virtual_selected_rows[0]]
        print( f"Selected row: {selected_row}")
