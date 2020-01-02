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
from os.path import abspath
import sys

if not abspath('../utils/') in sys.path:
    sys.path.append(abspath('../utils/'))

    from myconfig import db_config

app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
        }
    ],
)


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


cols = [
    'date',
    'snow_water_equivalent_in_start_of_day_values',
    'precipitation_accumulation_in_start_of_day_values',
    'air_temperature_maximum_degf',
    'air_temperature_minimum_degf',
    'air_temperature_average_degf',
    'precipitation_increment_in'
]


state = 'ID'
site = 'Reynolds Creek'

sql_command = f'''SELECT {', '.join([str(col) for col
 in [*cols]])} FROM snotel WHERE state='{state}' AND site_name='{site}' '''

datos = query_load_data(sql_command)

app.layout = html.Div(
    id="root",
    children=[
        html.H1(
            children='Plotting Snotel Sites from Postgresql'
        ),
        html.Div(
            dcc.Graph(
                id='example-graph',
                animate=True,
                figure=dict(
                    data=[
                        dict(
                            x=datos['date'],
                            y=datos['snow_water_equivalent_in_start_of_day_values'],
                            type='scatter+markers',
                        )
                    ]
                )
            )
        )
    ])


@app.callback(
    Output('example-graph', 'figure'),
    # events=[Event('graph-update', 'interval')]
)
def update_graph_scatter():
    X = deque(maxlen=10)
    Y = deque(maxlen=10)

    labels = ['date', 'snow_water_equivalent_in_start_of_day_values']

    X = datos[labels[0]]
    Y = datos[labels[1]]

    fig = datos.iplot(
        kind='Scatter',
        x=labels['date'],
        y=labels['snow_water_equivalent_in_start_of_day_values'],
        asFigure=True,
        mode='lines+markers'
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
