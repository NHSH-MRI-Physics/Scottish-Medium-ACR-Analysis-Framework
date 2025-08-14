import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='input-box', type='text'),
    html.Button('Submit', id='button'),
    html.Div(id='output-div')
])

@app.callback(
    Output('output-div', 'children'),
    [Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')]
)
def update_output(n_clicks, value):
    return f'You entered: {value}'

if __name__ == '__main__':
    app.run(debug=True,port=1234,host='127.0.0.1')