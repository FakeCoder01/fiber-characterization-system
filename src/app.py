import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import base64
import cv2
from fos.fiber_optic_system import FiberCharacterizationSystem
from core.image_analysis import FiberImageProcessor
import plotly.express as px
from typing import Any

app = dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.MORPH],
               suppress_callback_exceptions=True,
               title="Characterization Tool for optical fibers",
               meta_tags=[{'name': 'viewport',
                          'content': 'width=device-width, initial-scale=1'}],)
server = app.server

# initializes the characterization system
system = FiberCharacterizationSystem()


upload_style = {
    'width': '100%',
    'height': '60px',
    'lineHeight': '60px',
    'borderWidth': '2px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'marginLeft': '10px',
    'marginRight': '10px',
    'marginTop': '5px',
    'color': 'black'
}


app.layout = dbc.Container([
    dcc.Store(id='session-store'),
    dcc.Interval(id='live-update', interval=100),
    
    dbc.Tabs([
        dbc.Tab(label="Live Monitoring", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Row(dcc.Graph(id='power-gauge'),),
                ], md=6),
                dbc.Col([
                    dbc.Row(dcc.Graph(id='alignment-view'),)
                ], md=6),
            ], style={'marginBottom' : '-40px', 'paddingBottom' : '0px', 'marginTop' : '-40px', 'paddingTop' : '0px'}),
            dbc.Row([
                dbc.Row(dcc.Graph(id='spectral-plot'), style={'marginTop' : '0px', 'paddingTop' : '0px'})
            ]) 
        ], style={'backgroundColor' : 'white'}, tab_style={'zIndex' : '99999', 'backgroundColor' : 'inherit'}),

        
        dbc.Tab(label="Image Analysis", children=[
            dcc.Upload(
                id='image-upload',
                children=html.Div(['Drag & Drop or ', html.A('Select Fiber Image')]),
                style=upload_style
            ),
            dbc.Row([
                dbc.Col(dcc.Graph(id='original-image'), md=6),
                dbc.Col(dcc.Graph(id='processed-image'), md=6)
            ]),
            html.Div(id='fiber-parameters')
        ], tab_style={'zIndex' : '99999', 'backgroundColor' : 'inherit'}),
        
        dbc.Tab(label="Reports", children=[
            html.Div(id='report-generation')
        ], tab_style={'zIndex' : '99999', 'backgroundColor' : 'inherit'})
    ])
], fluid=True, style={'backgroundColor' : 'white'})



@app.callback(
    [Output('power-gauge', 'figure'),
     Output('spectral-plot', 'figure'),
     Output('alignment-view', 'figure')],
    [Input('live-update', 'n_intervals')]
)
def update_live_data(_ : Any = None):

    if system.data_queue.empty():
        raise dash.exceptions.PreventUpdate
        
    data = []
    while not system.data_queue.empty():
        data.append(system.data_queue.get())
        
    wavelengths = [d['wavelength'] for d in data]
    powers = [d['power'] for d in data]
    
    # creates gauge figure
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=powers[-1],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-40, 0]},
               'bar': {'color': '#2a9fd6'}}
    ))
    
    # creates spectral plot
    spectral = go.Figure(data=go.Scatter(
        x=wavelengths, y=powers,
        line=dict(color='#2a9fd6', width=2)
    ))
    spectral.update_layout(
        title='Spectral Response',
        xaxis_title='Wavelength (nm)',
        yaxis_title='Power (dBm)'
    )
    
    # create alignment visualization
    alignment_fig = go.Figure(data=go.Scatterpolar(
        r=np.random.rand(10)*100,
        theta=np.linspace(0, 360, 10),
        fill='toself'
    ))
    
    return gauge, spectral, alignment_fig

@app.callback(
    [Output('original-image', 'figure'),
     Output('processed-image', 'figure'),
     Output('fiber-parameters', 'children')],
    [Input('image-upload', 'contents')]
)
def analyze_image(content):
    if not content:
        return go.Figure(), go.Figure(), ""
        
    # processes image
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    img = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
    
    # analyzes fiber
    analyzer = FiberImageProcessor(img)
    core_clad = analyzer.detect_core_cladding()
    
    # creates figures
    orig_fig = px.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    processed_fig = px.imshow(analyzer.processed, binary_string=True)
    
    # creates parameter display
    params = dbc.Card([
        dbc.CardHeader("Measured Parameters"),
        dbc.CardBody([
            dbc.ListGroup([
                dbc.ListGroupItem(f"Core Diameter: {core_clad['core']['diameter']:.2f} µm"),
                dbc.ListGroupItem(f"Cladding Diameter: {core_clad['cladding']['diameter']:.2f} µm"),
                dbc.ListGroupItem(f"MFD: {analyzer.calculate_mfd():.2f} µm")
            ])
        ])
    ])
    
    return orig_fig, processed_fig, params



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
