import dash
from dash import html

dash.register_page(__name__,name='Test History')

layout = html.Div([
    html.H1('This is the text history page'),
    html.Div('This is our text history content.'),
])