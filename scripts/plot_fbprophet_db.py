import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from os.path import abspath
import sys
import psycopg2
import pandas as pd
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


sql_command = f"SELECT * FROM snotel_fbprophet WHERE state='ID' AND site_name='Bogus Basin' "

fb_datos = query_load_data(sql_command).sort_values(by='date')

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

# upper_bound = go.Scatter(
#     name='Upper Bound',
#     x=fb_datos['date'],
#     y=fb_datos['yhat_upper'],
#     mode='lines',
#     marker=dict(color='#444'),
#     line=dict(width=0),
#     fillcolor='rgba(68,68,68,0.3)',
#     fill='tonexty'
# )

trace = go.Scatter(
    name='Yhat',
    x=fb_datos['date'],
    y=fb_datos['yhat'],
    mode='lines',
    line=dict(color='rgb(31, 119, 180)'),
    fillcolor='rgba(68, 68, 68, 0.3)',
    # fill='tonexty'
)


# lower_bound = go.Scatter(
#     name='Lower Bound',
#     x=fb_datos['date'],
#     y=fb_datos['yhat_lower'],
#     mode='lines',
#     marker=dict(color='#444'),
#     line=dict(width=0),
#     fillcolor='rgba(68,68,68,0.3)',
# )



plot_variable = 'yhat_upper'
dash_app.layout = html.Div(
    id="root",
    children = [
        dcc.Graph(
            figure=dict(
                data=[
                    upper_bound,
                    trace,
                    # lower_bound
                    #     dict(
                    #         x=fb_datos['date'],
                    #         y=fb_datos[plot_variable],
                    #         type='scatter',
                    #     )
                ],
                layout=go.Layout(
                    # title = f'{fb_datos["state"].unique()[0]}:' + \
                    # f' {fb_datos["site_name"].unique()[0]}',
                    paper_bgcolor = 'rgba(0,0,0,0)',
                    plot_bgcolor = 'rgba(0,0,0,0.1)',
                    yaxis=dict(
                        range=(
                            -3,
                            fb_datos[plot_variable].max(),
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
                ),
            ),
        ),
    ],
)


if __name__ == "__main__":
    dash_app.run_server(debug=True, port=5555)
