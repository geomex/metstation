import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from os.path import abspath
import sys
import psycopg2
import pandas as pd
import datetime as dt
if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))
    from myconfig import db_config


def query_load_data(sql_command=None):
    conn = psycopg2.connect(
        host=db_config['host'],
        user=db_config['user'],
        password='',
        dbname=db_config['dbname']
    )
    
    datos = pd.read_sql(sql_command, conn)
    datos.sort_index(inplace=True)
    conn.close()
    return datos

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

state = 'ID'
sql_command = f'''SELECT * FROM snotel 
WHERE state='{state}'
AND snow_water_equivalent_in_start_of_day_values > 0 '''

datos = query_load_data(sql_command).sort_values(by='date')

year_value = (2011, 2015)
datos['site_name_id'] = datos['site_name'] + " " + datos['site_id'].astype(str)
datos['year'] = datos\
    .date\
    .map(
        lambda x: int(x.strftime('%Y'))
    )


mask = (
    (datos['year'] > year_value[0]) &
    (datos['year'] < year_value[1])
)

YEARS = list(datos['year'].unique())

datos=datos.loc[mask]


import plotly.express as px
# hist = px.histogram(
#     datos,
#     x="snow_water_equivalent_in_start_of_day_values",
#     # marginal="box"
# )



hist = go.Histogram(
    name='SWE Distributions',
    x=datos['snow_water_equivalent_in_start_of_day_values'],
    histnorm='probability',
    # marginal="box"
    # color='site_name_id'
)


dash_app.layout = html.Div(
    id="state-swe_dist",
    children = [
        html.Div(
            id='daterange-container',
            children=[
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
            ],
        ),
        html.Br(),html.Br(),
        html.Div(
            id='datepicker-container',
            children = [
                dcc.DatePickerRange(
                    id='datepickerrange',
                    start_date=datos['date'].min(),
                    end_date=datos['date'].max(),
                    display_format='MMM D YYYY',
                    number_of_months_shown=2,
                    updatemode='bothdates',
                    end_date_placeholder_text="End Period",
                ),
            ],
        ),        
        html.Div(
            id='swe-dist-container',
            children=[
                dcc.Graph(
                    id='swe-dist',
                    figure=dict(),
                ),
            ],
        ),
    ],
)

@dash_app.callback(
    [Output('datepickerrange', 'start_date'),
     Output('datepickerrange', 'end_date')],
     # Output('datepickerrange', 'min_date_allowed'),
     # Output('datepickerrange', 'max_date_allowed')],
    [Input('years-slider','value')]
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
    [Input('datepickerrange','start_date'),
     Input('datepickerrange', 'end_date')]
)
def swe_dist_update(start_date, end_date):
    if type(start_date) is dt.datetime:
        start_date = start_date.strftime('%m/%d/%Y')
    if type(end_date) is dt.datetime:
        end_date = end_date.strftime('%m/%d/%Y')
        
    state = 'ID'
    sql_command = f'''SELECT * FROM snotel 
    WHERE state='{state}'
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
            title=dict(
                text=state
            ),
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
                t=0, b=30, r=0, l=40
            )  
        ),
    )
    
    return figure


if __name__ == "__main__":
    dash_app.run_server(debug=True, port=5555)
