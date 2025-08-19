import dash
from dash import Dash, dcc, html, Input, Output, callback
from plotly_calplot import calplot
import pandas as pd
import numpy as np
dash.register_page(__name__,name='Test Explorer')

#Make some dummy date
dummy_start_date = "2019-01-01"
dummy_end_date = "2021-10-03"
full_df = pd.DataFrame({
    "ds": pd.date_range(dummy_start_date, dummy_end_date),
    "value": np.random.randint(low=0, high=30,
size=(pd.to_datetime(dummy_end_date) - pd.to_datetime(dummy_start_date)).days + 1,),
})

#Get years in the date
years = full_df['ds'].dt.year.unique()
Dropdown =  dcc.Dropdown(
        id='Date-Dropdown',
        options=years,
        value=years[0],
        clearable=False,
        style={'width': '300px'}
    )
filtered_df = full_df[full_df['ds'].dt.year == years[0]]


#Make a plot to start with using the first year
fig = calplot(
    filtered_df,
    x="ds",
    y="value",
    years_title=True,
    dark_theme=True
)

layout = html.Div([
    html.H1('Test Explorer'),
    html.Div('Choose a year.'),
    Dropdown,
    dcc.Graph(figure=fig,id="Date-Plot")
])


@dash.callback(
    Output('Date-Plot', 'figure'),
    Input('Date-Dropdown', 'value')
)
def update_figure(selected):
    filtered_df = full_df[full_df['ds'].dt.year == selected]
    fig = calplot(
    filtered_df,
    x="ds",
    y="value",
    years_title=True,
    dark_theme=True
    )
    return fig


@dash.callback(
    #Output('Date-Plot', 'selectedData'),
    Input('Date-Plot', 'clickData')
)
def display_click(clickData):
    if clickData is not None:
        date = clickData['points'][0]['customdata'][0]
    print(date) #output this to a table or something