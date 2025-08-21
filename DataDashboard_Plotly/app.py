import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc  # Add this import


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CYBORG])

NavbarObj = []
for page in dash.page_registry.values():
    NavbarObj.append(dbc.NavItem(dbc.NavLink(page['name'], href=page["relative_path"])))
navbar = dbc.NavbarSimple(
    children=NavbarObj,
    brand="Med ACR Data Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    navbar,
    dash.page_container 
])

if __name__ == '__main__':
    app.run(debug=True)