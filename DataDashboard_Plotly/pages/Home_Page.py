import dash
from dash import html

dash.register_page(__name__, path='/',name='Home Page')

layout = html.Div([
    html.H1('Medium ACR Data Dashboard'),
    html.Img(
        src=dash.get_asset_url('SplashScreen.jpg'),
        alt='image',
        style={'width': '20%', 'height': 'auto'}),
    html.Div('This is where i will describe what the dashboard does and how to use it.'),
    
])