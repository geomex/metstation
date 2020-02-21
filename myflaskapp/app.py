''' Description:
by: Joel A. Gongora
date:12/29/2019
'''

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import psycopg2
from collections import deque
import pandas as pd
# import dash_bootstrap_components as dbc
from os.path import abspath
import sys
import datetime as dt
from flask_app import my_app



# if not abspath('../utils/') in sys.path:
#     sys.path.append(abspath('../utils/'))
from myconfig import db_config

dash_app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ],
    server=my_app,
    url_base_pathname='/snotel_dashboard/'
)

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# Joel's Version #
# mapbox_access_token = "pk.eyJ1IjoiamdvbmdvcmEiLCJhIjoiY2p6bDd0c2c3MHNycDNjcHBoanE3bWxvdCJ9.96Kl63kGmTtmlsvTHKu6Ig"
# mapbox_style = "https://api.mapbox.com/styles/v1/jgongora/ck4spcbw01zc01cmk4dbgkzrm.html?fresh=true&title=copy&access_token=pk.eyJ1IjoiamdvbmdvcmEiLCJhIjoiY2p6bDd0c2c3MHNycDNjcHBoanE3bWxvdCJ9.96Kl63kGmTtmlsvTHKu6Ig#14.0/37.268600/-112.942500/0"

server = dash_app.server

def query_load_data(sql_command=None):
    conn = psycopg2.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        dbname=db_config['dbname']
    )
    
    datos = pd.read_sql(sql_command, conn)
    datos.sort_index(inplace=True)
    conn.close()
    return datos


cols = [
    'date',
    'snow_water_equivalent_in_start_of_day_values',
    'precipitation_accumulation_in_start_of_day_values',
    'air_temperature_maximum_degf',
    'air_temperature_minimum_degf',
    'air_temperature_average_degf',
    'precipitation_increment_in',
    'site_name',
    'state'
]

# ------------ #
# Query States #
# ------------ #

def return_state_db():
    query_state = '''SELECT state FROM snotel '''
    estados = query_load_data(
        query_state
    )['state'].unique().tolist()
    return estados


# --------------------------- #
# Query Single State and Site #
# --------------------------- #

state = 'ID'
site = 'Bogus Basin'
site_id = '978'

sql_command = f'''SELECT {', '.join([str(col) for col
in [*cols]])} FROM snotel WHERE state='{state}'  AND site_name='{site}' 
AND site_id='{site_id}' '''

datos = query_load_data(sql_command).sort_values(by='date')
datos['year'] = datos.date.map(lambda x: int(x.strftime('%Y')))
YEARS = list(datos['year'].unique())

sql_command = f'''SELECT * FROM snotel_fbprophet 
WHERE state='{state}' AND site_name='{site}' '''

fb_datos = query_load_data(sql_command).sort_values(by='date')

fb_datos.loc[fb_datos['yhat'] < 0, 'yhat'] = 0
upper_bound = go.Scatter(
    name='Upper Bound',
    x=fb_datos['date'],
    y=fb_datos['yhat_upper'],
    mode='lines',
    marker=dict(color='#444'),
    line=dict(width=0),
    fillcolor='rgba(68,68,68,0.3)',
    fill='tonexty'
)

trace = go.Scatter(
    name='Yhat',
    x=fb_datos['date'],
    y=fb_datos['yhat'],
    mode='lines',
    line=dict(color='rgb(31, 119, 180)'),
    fillcolor='rgba(68, 68, 68, 0.3)',
    fill='tonexty'
)


lower_bound = go.Scatter(
    name='Lower Bound',
    x=fb_datos['date'],
    y=fb_datos['yhat_lower'],
    mode='lines',
    marker=dict(color='#444'),
    line=dict(width=0),
    fillcolor='rgba(68,68,68,0.3)',
)

hist = go.Histogram(
    name='SWE Distributions',
    x=datos['snow_water_equivalent_in_start_of_day_values'],
    histnorm='probability',
    # marginal="box"
    # color='site_name_id'
)

# --------------- #
# Query Locations #
# --------------- #
cols_locs = [
    'ntwk', 'state', 'site_name',
    'ts', 'start', 'lat',
    'lon', 'elev', 'county', 'huc'
]

sql_command = f'''SELECT {', '.join([str(col) for col
in [*cols_locs]])} FROM snotel_locs WHERE state='{state}' '''

datos_locs = query_load_data(sql_command)

dash_app.layout = html.Div(
    id="root",
    children=[
        # ------------------ #
        # Title of Dashboard #
        # ------------------ #        
        html.Div(
            id="header",
            children=[
                html.Img(
                    id="nasalogo",
                    src=dash_app.get_asset_url("nasa_logo.png"),
                    style = dict(
                        height='6%',
                        width='6%'
                    )
                ),
                html.Img(
                    id="logo",
                    src=dash_app.get_asset_url(
                        "eri_2018_logo_stacked_medium_white.png"
                    ),
                    style = dict(
                        height='16%',
                        width='16%'
                    )
                ),
                html.Img(
                    id="bsulogo",
                    src=dash_app.get_asset_url("bsulogo_allwhite.png"),
                    style = dict(
                        height='6%',
                        width='6%'
                    )
                ),
                html.H4(children="NRCS Snotel: Snow Accumulation Graphs"),
                html.P(
                    id="description",
                    children="Snotel Meteorlogical Station Application",
                ),
            ],
        ),
        # ---------------------- #
        # Left Column Container  #
        # ---------------------- #
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            # ------------- #
                            # State Selector #
                            # ------------- #                            
                            id='state-container',
                            children=[
                                html.P(
                                    id='state-container-title',
                                    children=[
                                        html.P(
                                            "Select the State:",
                                        ),
                                    ],
                                ),
                                dcc.Dropdown(
                                    id="state-dropdown",                                    
                                    options=[
                                        {'label': i, 'value': i}
                                        for i in return_state_db()
                                    ],
                                    value='ID'
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    'Map of Snotel Locations',
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="snotel_map",
                                    figure=dict(
                                        layout=go.Layout(
                                            margin={'b': 0}
                                        )
                                    ),
                                ),
                            ],#style = {
                            #     "border-style": "solid",
                            #     "height": "50%",
                            #     # "width": "100%",
                            #     "fontsize":16
                            # },
                        ),
                        # html.Div(
                        #     id="state-swe-dist-container",
                        #     children = [
                        #         html.H5('State SWE Distribution'),
                        #         dcc.Graph(
                        #             id='state-swe-dist',
                        #             figure=dict(),
                        #         ),
                        #     ],
                        # ),
                        html.Br(),
                        html.Div(
                            id="year-state-swe-dist",
                            children = [
                                html.H5(
                                    'State SWE Distribution by Date'
                                ),
                            ],
                        ),
                        html.Div(
                            id='daterange-container',
                            children=[
                                html.P(
                                    id="swe-daterange-text",
                                    children="Drag the slider to change the year:",
                                ),                                        
                                dcc.RangeSlider(
                                    id="swe-dist-years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[min(YEARS), max(YEARS)],
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {
                                                "color": "#7fafdf",
                                                "writing-mode": "vertical-rl"
                                            },
                                        }
                                        for year in YEARS                                        
                                    },
                                ),
                            ], # style={
                            #     'text-orientation': 'sideways', 
                            #     "border-style": "solid",
                            #     # 'height':'100%'
                            # },
                        ),
                        html.Br(), html.Br(),
                        html.Div(
                            id='datepicker-container',
                            children = [
                                dcc.DatePickerRange(
                                    id='swe-dist-datepickerrange',
                                    start_date=datos['date'].min(),
                                    end_date=datos['date'].max(),
                                    display_format='MMM D YYYY',
                                    number_of_months_shown=2,
                                    updatemode='bothdates',
                                    end_date_placeholder_text="End Period",
                                ),
                            ],style={"padding-left": '25%'}
                        ),
                        html.Br(), html.Br(),
                        html.Div(
                            id='swe-dist-container',
                            children=[
                                dcc.Graph(
                                    id='swe-dist',
                                    figure=dict(),
                                ),
                            ],
                        ),
                    ],style = {
                        "border-style": "solid",
                        "height": "210%",
                        "width": "100%",
                    },
                ),
                # ---------- #
                # SWE Curves #
                # ---------- #
                html.Div(
                    id="right_column",
                    children= [
                        # ------------- #
                        # Site Selector #
                        # ------------- #                        
                        html.Div(
                            id='site-container',
                            children=[
                                html.P(
                                    id='site-container-title',                                    
                                    children=[
                                        html.P("Select a Site:")
                                    ],
                                ),
                                dcc.Dropdown(
                                    id="site-dropdown",                                    
                                    options=[
                                    ],
                                    value=''
                                ),
                            ],
                        ),
                        # ------------- #
                        # Year Selector #
                        # ------------- #                        
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.RangeSlider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[min(YEARS), max(YEARS)],
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {
                                                "color": "#7fafdf",
                                                "writing-mode": "vertical-rl"
                                            },
                                        }
                                        for year in YEARS                                        
                                    },
                                ),
                            ],#style={
                            #     'text-orientation': 'sideways', 
                            #     "border-style": "solid",
                            # },
                        ),
                        # ----------------- #
                        # Snotel Swe Curves #
                        # ----------------- #                        
                        html.Div(
                            children = [
                                html.H5('Measured SWE for Snotel Site Selected'),
                                dcc.Graph(
                                    id='swe-plot',
                                    animate=True,
                                    figure=dict(
                                        data=[
                                            dict(
                                                x=datos['date'],
                                                y=datos['snow_water_equivalent_in_start_of_day_values'],
                                                type='scatter',
                                            )
                                        ],
                                        layout=go.Layout(
                                            paper_bgcolor = 'rgba(0,0,0,0)',
                                            plot_bgcolor = 'rgba(0,0,0,0.1)',
                                            yaxis=dict(
                                                range=(
                                                    datos['snow_water_equivalent_in_start_of_day_values'].min(),
                                                    datos['snow_water_equivalent_in_start_of_day_values'].max(),
                                                ),
                                                title='Snow Water Equivalent (inches)',
                                                titlefont = dict(
                                                    color='lightgrey'
                                                ),
                                                tickfont = dict(
                                                    color='lightgrey'
                                                ),
                                            ),
                                            xaxis = dict(
                                                title = 'Dates',
                                                titlefont = dict(
                                                    color='lightgrey'
                                                ),
                                                tickfont = dict(
                                                    color='lightgrey'
                                                ),                                            
                                            ),
                                            scene=dict(
                                                xaxis=dict(
                                                    # backgroundcolor="rgb(200, 200, 230)",
                                                    gridcolor="rgba(0,0,0, 0.1)",
                                                    showbackground=True,
                                                    zerolinecolor="rgba(0,0,0)",
                                                    tickwidth=1,
                                                    tickfont=dict(
                                                        color="white",
                                                    ),
                                                ),
                                                yaxis=dict(
                                                    # backgroundcolor="rgb(200, 200, 230)",
                                                    gridcolor="rgba(0,0,0, 0.1)",
                                                    showbackground=False,
                                                    zerolinecolor="rgba(0,0,0,0.1)",
                                                    tickwidth=1,
                                                    tickfont=dict(
                                                        color="white",
                                                    ),
                                                    title='Snow Water Equivalent'
                                                ),                            
                                            ),
                                            margin={'t':0},
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        # ----------------------- #
                        # Prophet Swe Predictions #
                        # ----------------------- #                        
                        html.Div(
                            # id="root",
                            children = [
                                html.H5('Prophet Forecast'),        
                                dcc.Graph(
                                    id='forecast-graph',
                                    animate=True,
                                    figure=dict(
                                        data=[
                                            upper_bound,
                                            trace,
                                            lower_bound
                                        ],
                                        layout=go.Layout(
                                            margin={'t':0, 'b': 0},                                            
                                        ),
                                    ),
                                ),
                            ],
                        ),
                     ],  style={
                        "border-style": "solid",
                        "width": "100%",
                        "height": "150%"
                    },
                ),
            ], 
        ),
    ],
)


@dash_app.callback(
    [Output('swe-dist-datepickerrange', 'start_date'),
     Output('swe-dist-datepickerrange', 'end_date')],
    # Output('datepickerrange', 'min_date_allowed'),
    # Output('datepickerrange', 'max_date_allowed')],
    [Input('swe-dist-years-slider','value')]
)
def datepicker_update(anos):
    state = 'ID'
    start_date = dt.datetime.strptime('10/01/' + str(anos[0]), '%m/%d/%Y') #dias['min'].tolist()[0]
    end_date =  dt.datetime.strptime('09/30/' + str(anos[1]), '%m/%d/%Y') #dias['max'].tolist()[0]
    sql_command = f'''SELECT MIN(date), MAX(date) 
    from snotel WHERE state='ID' AND date BETWEEN 
    '{start_date}' AND '{end_date}';'''
    dias = query_load_data(sql_command).dropna()
    min_date_allowed = dias['min'].tolist()[0]
    max_date_allowed =  dias['max'].tolist()[0]    
    return [start_date, end_date] #, min_date_allowed, max_date_allowed


@dash_app.callback(
    Output('swe-dist', 'figure'),
    [Input('swe-dist-datepickerrange','start_date'),
     Input('swe-dist-datepickerrange', 'end_date'),
     Input('state-dropdown', 'value')]
)
def swe_dist_update(start_date, end_date, state_value):
    if type(start_date) is dt.datetime:
        start_date = start_date.strftime('%m/%d/%Y')
    if type(end_date) is dt.datetime:
        end_date = end_date.strftime('%m/%d/%Y')
        
    # state = 'ID'
    sql_command = f'''SELECT * FROM snotel 
    WHERE state='{state_value}'
    AND snow_water_equivalent_in_start_of_day_values > 0 
    AND date between  '{start_date}' AND '{end_date}' '''
        
    datos = query_load_data(sql_command).sort_values(by='date')
        
    hist = go.Histogram(
        name='SWE Distributions',
        x=datos['snow_water_equivalent_in_start_of_day_values'],
        histnorm='probability',
    )
        
    figure=dict(
        data=[hist],
        layout=go.Layout(
            # title=dict(
            #     text=state_value
            # ),
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            scene=dict(
                xaxis=dict(
                    gridcolor="rgba(0,0,0, 0.1)",
                    showbackground=True,
                    zeroline=True,
                    zerolinecolor="rgba(0,0,0)",
                    tickwidth=1,
                    tickfont=dict(
                        color="black",
                    ),
                ),
                yaxis=dict(
                    backgroundcolor="rgb(200, 200, 230)",
                    gridcolor="rgba(0,0,0, 0.1)",
                    showbackground=False,
                    zeroline=True,
                    zerolinecolor="rgba(0,0,0,0.1)",
                    tickwidth=1,
                    tickfont=dict(
                        color="black",
                    ),
                ),
            ),
            yaxis=dict(
	        title=dict(
                    text='Probability',
                    font=dict(
                        color='#7f7f7f'
                    ),
                ),
                range=[0, 0.1],
            ),
            xaxis=dict(
		title=dict(
                    text='Snow Water Equivalent [inches]',
                    font=dict(
                        color='#7f7f7f'
                    ),
                ),
            ),
            margin=dict(
                t=15, b=30, r=0, l=40
            )  
        ),
    )
        
    return figure


# @dash_app.callback(
        #     Output("state-swe-dist", "figure"),
        #     [
        #         Input("state-dropdown", "value"),
        #         Input("years-slider", "value")
        #     ]
        # )
        # def state_swe_dist_update(state_value, year_value):
        #     sql_command = f"SELECT * FROM snotel WHERE state='{state_value}' " + \
        #         "AND snow_water_equivalent_in_start_of_day_values > 0"
    
#     temp_datos = query_load_data(sql_command).sort_values(by='date')
        #     temp_datos['year'] = temp_datos\
        #         .date\
        #         .map(
        #             lambda x: int(x.strftime('%Y'))
        #         )
        #     mask = (
        #         (temp_datos['year'] > year_value[0]) &
        #         (temp_datos['year'] < (year_value[1]))
        #     )
    
#     temp_datos=temp_datos.loc[
        #         mask
        #     ]
        #     # temp_datos['site_name_id'] = temp_datos['site_name']
        #     hist = go.Histogram(
        #         name='SWE Distributions',
        #         x=temp_datos['snow_water_equivalent_in_start_of_day_values'],
        #         histnorm='probability',
        #     )

#     figure=dict(
        #         data=[hist],
        #         layout=go.Layout(
        #             title=dict(
        #                 text=state_value
        #             ),
        #             paper_bgcolor = 'rgba(0,0,0,0)',
        #             plot_bgcolor = 'rgba(0,0,0,0)',
        #             scene=dict(
        #                 xaxis=dict(
        #                     gridcolor="rgba(0,0,0, 0.1)",
        #                     showbackground=True,
        #                     zeroline=True,
        #                     zerolinecolor="rgba(0,0,0)",
        #                     tickwidth=1,
        #                     tickfont=dict(
        #                         color="black",
        #                     ),
        #                 ),
        #                 yaxis=dict(
        #                     backgroundcolor="rgb(200, 200, 230)",
        #                     gridcolor="rgba(0,0,0, 0.1)",
        #                     showbackground=False,
        #                     zeroline=True,
        #                     zerolinecolor="rgba(0,0,0,0.1)",
        #                     tickwidth=1,
        #                     tickfont=dict(
        #                         color="black",
        #                     ),
        #                 ),
        #             ),
        #             yaxis=dict(
        # 	        title=dict(
        #                     text='Probability',
        #                     font=dict(
        #                         color='#7f7f7f'
        #                     ),
        #                 ),
        #             ),
        #             xaxis=dict(
        # 		title=dict(
        #                     text='Snow Water Equivalent [inches]',
        #                     font=dict(
        #                         color='#7f7f7f'
        #                     ),
        #                 ),
        #             ),
        #             margin=dict(
        #                 t=0, b=30, r=0, l=40
        #             )
            
#         ),
        #     )
        #     return figure

@dash_app.callback(
    Output("forecast-graph", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("site-dropdown", "value"),
        Input("years-slider", "value")        
    ]
)
def fbprophet_update(state_value, site_value, year_value):
    if len(site_value.split(" ")) >= 3:
        site_name = " ".join(site_value.split(" ")[:-1])
    else:
        site_name = site_value.split(" ")[0]
        site_id = site_value.split(" ")[-1]    
        
    sql_command = f'''SELECT * FROM snotel_fbprophet 
    WHERE state='{state_value}' AND site_name='{site_name}' '''
        
    fb_datos = query_load_data(sql_command).sort_values(by='date')
    fb_datos.dropna(inplace=True, axis=0)
    fb_datos['year'] = fb_datos.date.map(lambda x: int(x.strftime('%Y')))
    
    fb_datos = fb_datos.loc[
        (fb_datos['year'] > year_value[0]) &
        (fb_datos['year'] < year_value[1])
    ]

    fb_datos.loc[fb_datos['yhat']<0, 'yhat'] = 0
    upper_bound = go.Scatter(
        name='Upper Bound',
        x=fb_datos['date'].tolist() + \
        fb_datos.sort_values(
            by='date', ascending=False
        )['date'].tolist(),
            
        y=fb_datos['yhat_upper'].tolist() + \
            fb_datos.sort_values(
                by='date', ascending=False
            )['yhat_lower'].tolist(),
            
        mode='lines',
            marker=dict(color='#444'),
            line=dict(width=0),
            fillcolor='rgba(200, 5, 214, 0.3)',#'rgba(68,68,68,0.3)',
            fill='tozerox'
        )
        
    trace = go.Scatter(
        name='Yhat',
        
        x=fb_datos['date'],
        # fb_datos.sort_values(
        #     by='date', ascending=False
        # )['date'].tolist(),
        
        y=fb_datos['yhat'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(68, 68, 68, 0.3)',
        # fill='tonexty'
    )

    layout = go.Layout(
	# title = f'{state_value}: {site_name}',
	paper_bgcolor = 'rgba(0,0,0,0)',
	plot_bgcolor = 'rgba(0,0,0,0)',
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="rgba(0,0,0, 0.1)",
                zerolinecolor="rgba(0,0,0)",                
                showbackground=False,
                tickwidth=1,
                tickfont=dict(
                    color="white",
                ),
            ),
            yaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="rgba(0,0,0, 0.1)",
                zerolinecolor="rgba(0,0,0,0.1)",                
                showbackground=False,
                tickwidth=1,
                tickfont=dict(
                    color="white",
                ),
                title='SWE'
            ),                            
        ),            
    )

    figure=dict(
        data=[
            upper_bound,
            trace
        ],
        layout=layout
    )

    return figure

    
    

@dash_app.callback(
    Output("snotel_map", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("site-dropdown", "value")
    ]
)
def update_snotel_map(state_value, site_value):
    cols = [
        'ntwk', 'state', 'site_name',
        'ts', 'start', 'lat',
        'lon', 'elev', 'county', 'huc'
    ]

    sql_command = f'''SELECT {', '.join([str(col) for col
    in [*cols]])} FROM snotel_locs WHERE state='{state_value}' '''

    datos_locs = query_load_data(sql_command)

    if len(site_value.split(" ")) >= 3:
        site_name = " ".join(site_value.split(" ")[:-1])
    else:
        site_name = site_value.split(" ")[0]

    site_id = site_value.split(" ")[-1]

    site_lat, site_lon = zip(
        *datos_locs.loc[
            datos_locs['site_name'].str.contains(site_name) &
            datos_locs['site_name'].str.contains(site_id)
        ][['lat','lon']].values
    )

    data=[
        go.Scattermapbox(
            lat=datos_locs["lat"],
            lon=datos_locs["lon"],
            text=datos_locs["site_name"],
            name='Snotel Sites'
        ),
        go.Scattermapbox(
            lat=site_lat,
            lon=site_lon,
            text=site_value,
            marker=go.scattermapbox.Marker(
                size=14
            ),
            name=site_value
        )
    ]

    layout=go.Layout(
	paper_bgcolor = 'rgba(0,0,0,0)',
	plot_bgcolor = 'rgba(0,0,0,0)',
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            center=dict(
                lat=datos_locs["lat"].mean(),
                lon=datos_locs["lon"].mean()
            ),
            zoom=3.5,
        ),
        # autosize=True,
        margin={'t':0, 'b':0, 'r':0, 'l':0},
        legend=dict(
            orientation='h',
            font=dict(
                color='white',
                )
        )
    )

    figure = {
        'data': data,
        'layout': layout
    }
        
    return figure


@dash_app.callback(
    [Output("site-dropdown", "options"),
     Output("site-dropdown", "value")],
    [Input("state-dropdown", "value")]
)
def update_site_dropdown(state_value):
    cols = [
        'date',
        'snow_water_equivalent_in_start_of_day_values',
        'precipitation_accumulation_in_start_of_day_values',
        'air_temperature_maximum_degf',
        'air_temperature_minimum_degf',
        'air_temperature_average_degf',
        'precipitation_increment_in',
        'site_name',
        'site_id',
        'state'
    ]

    sql_command = f'''SELECT {', '.join([str(col) for col
    in [*cols]])} FROM snotel WHERE state='{state_value}' '''

    datos = query_load_data(sql_command).sort_values(by='date')
    datos['year'] = datos.date.map(lambda x: int(x.strftime('%Y')))

    tmp = datos[
        ['state','site_id','site_name']
    ].drop_duplicates().sort_values(by='site_name')

    options = [ {'label': " ".join(i), 'value': " ".join(i)}
                for i in sorted(
                        zip(
                            tmp.loc[
                                tmp['state'] == state_value
                            ]['site_name'],
                            tmp.loc[
                                tmp['state'] == state_value
                            ]['site_id'].map(str)
                        )
                )
    ]
    value = options[0]
    return  options, value['value']



@dash_app.callback(
    Output("swe-plot", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("site-dropdown", "value"),        
        Input("years-slider", "value")
    ],
    # events=[Event('graph-update', 'interval')]
)
def update_graph_scatter(state_value, site_value, year):

    labels = ['date', 'snow_water_equivalent_in_start_of_day_values']

    data = []                   # setup data for callback

    if len(site_value.split(" ")) >= 3:
        site_name = " ".join(site_value.split(" ")[:-1])
    else:
        site_name = site_value.split(" ")[0]
        
    site_id = site_value.split(" ")[-1]
    sql_command = f'''SELECT {', '.join([str(col) for col
    in [*cols]])} FROM snotel WHERE state='{state_value}'
    AND site_name='{site_name}' AND site_id='{site_id}' '''

    datos = query_load_data(sql_command).sort_values(by='date')
    datos['year'] = datos.date.map(lambda x: int(x.strftime('%Y')))    

    state_data = datos.loc[datos['state'] == state_value]

    data = [
        dict(
            x=state_data['date'].loc[
                (state_data['year'] > year[0]) & (state_data['year'] < year[1])
            ],
            y=state_data['snow_water_equivalent_in_start_of_day_values'].loc[
                (state_data['year'] > year[0]) & (state_data['year'] < year[1])
            ],
            type='scatter',
            hoverinfo='x'+'y'
        )
    ]
    layout = go.Layout(
	title = f'{state_value}: {site_value}',
	paper_bgcolor = 'rgba(0,0,0,0)',
	plot_bgcolor = 'rgba(0,0,0,0)',
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="rgba(0,0,0)",
                showbackground=True,
                tickwidth=2,
                tickfont=dict(
                    color="white",
                ),
            ),
            yaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="rgba(0,0,0)",
                showbackground=True,
                tickwidth=2,
                tickfont=dict(
                    color="white",
                ),
                title='SWE'
            ),                            
        ),
        autosize=True,
        margin={'t': 0}
    )
    
    figure = {
        'data': data,
        'layout': layout
    }

    return figure


if __name__ == "__main__":
        dash_app.run_server(debug=True, port=8000)
