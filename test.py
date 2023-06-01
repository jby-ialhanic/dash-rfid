# from dash import Dash, html
# import pyodbc
# import pandas as pd
from dash import Dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
import plotly.graph_objs as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import plotly.express as px
from collections import deque
import pandas as pd
import pyodbc


#db stuff
# conn = pyodbc.connect('Driver={Devart ODBC Driver for PostgreSQL};'
#                       'Server=10.15.72.15;'
#                       'Port=5432;'
#                       'Database=postgres;'
#                       'User ID=tooltracker;'
#                       'Password=crushingit;'
#                       'Trusted_Connection=yes;')

# cursor = conn.cursor()
# cursor.execute('SELECT * FROM public."rfidData" LIMIT 100')
# row = cursor.fetchone()
# while row:
#     print(row[7])
#     row = cursor.fetchone()
def update_scatterplot():
    df = pd.DataFrame()
def update_graph_scatter():
    dataSQL = [] #empty list
    X_Var = deque(maxlen=10)
    Y_Var = deque(maxlen=10)

    sql_conn = pyodbc.connect('Driver={Devart ODBC Driver for PostgreSQL};'
                      'Server=10.15.72.15;'
                      'Port=5432;'
                      'Database=postgres;'
                      'User ID=tooltracker;'
                      'Password=crushingit;'
                      'Trusted_Connection=yes;')
    cursor = sql_conn.cursor()
    cursor.execute('SELECT "peakRssiCdbm", "frequency" FROM public."rfidData" LIMIT 100')
    rows = cursor.fetchall()
    i = 0
    for row in rows:
        i += 1
        dataSQL.append(list(row))
        labels = ['peakRssiCdbm', 'frequency']
        df = pd.DataFrame.from_records(dataSQL, columns = labels)
        X_Var = df['frequency']
        Y_Var = df['peakRssiCdbm']
    
    data = plotly.graph_objs.Scatter(
        x = list(X_Var),
        y = list(Y_Var),
        name='Scatter',
        mode= 'lines+markers'
    )
    return {'data': [data], 'layout' : go.Layout(
                                    xaxis = dict(range=[min(X_Var), max(X_Var)]),
                                    yaxis = dict(range=[min(Y_Var), max(Y_Var)]),
    )}

scatterdf = update_graph_scatter()
print(scatterdf)
name_title = 'RSSI Data from PostgreSQL server'
app = Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Read near real-time data from server on Scatterplot'),

    dcc.Graph(
        id = 'scatter-plot',
        figure = px.scatter(scatterdf, title="RSSI_Scatter", y='RSSI', x='frequency',),
        animate = True
    ),
    dcc.Interval(
        id = 'graph-update',
        interval = 1*500
    ),
])

@app.callback(
    Output('scatterplot', 'figure'),
    Input('scatterplot', 'id'))

def update_output_div(input_value):
    return f'Output: {input_value}'


if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1')


#app stuff
# app = Dash(__name__)
# app.title = 'RSSI Plot'

# app.layout = html.Div([
#     html.Div(children='Hello World')
    
# ])

# if __name__ == '__main__':
#     app.run_server(debug=True,host = '127.0.0.1')




#5-31-23
# from dash import Dash, html
# import pyodbc
# import pandas as pd
# import dash
# from dash import Dash
# from dash.dependencies import Output, Input
# from dash import dcc
# from dash import html
# import plotly
# import plotly.graph_objs as go
# import dash_mantine_components as dmc
# import dash_bootstrap_components as dbc
# import plotly.express as px
# from collections import deque
# import pandas as pd
# import pyodbc
# import psycopg2
# import time

# app = dash.Dash(__name__)
# #db stuff
# conn = psycopg2.connect(
#     host = "10.15.72.15",
#     port = "5432",
#     database = "postgres",
#     user = "tooltracker",
#     password = "crushingit"
# )
# app.layout = html.Div([
#     html.H1('Scatterplot'),
#     dcc.Graph(
#         id = 'scatter-plot'
#         # figure = {
#         #     'data': [scatterplot],
#         #     'layout': {
#         #         'title': 'Scatterplot Test'
#         #     }
#         # }
#     ),
#     dcc.Interval(
#         id='interval-component',
#         interval=5*1000,
#         n_intervals=0
#     )
# ])
# # conn = pyodbc.connect('Driver={Devart ODBC Driver for PostgreSQL};'
# #                       'Server=10.15.72.15;'
# #                       'Port=5432;'
# #                       'Database=postgres;'
# #                       'User ID=tooltracker;'
# #                       'Password=crushingit;'
# #                       'Trusted_Connection=yes;')

# def update_DF():
#     cursor = conn.cursor()
#     cursor.execute('SELECT public."toolLocation"."toolId", x, y FROM public."toolLocation" JOIN (SELECT "toolId", MAX("ts") AS latest_timestamp FROM public."toolLocation" GROUP BY "toolId") subquery ON public."toolLocation"."toolId" = subquery."toolId" AND public."toolLocation"."ts" = subquery.latest_timestamp ORDER BY public."toolLocation"."toolId" ASC') #order by timestamp descending order
#     column_names = [desc[0] for desc in cursor.description]
#     results = cursor.fetchall()
#     pd_results = pd.DataFrame(results, columns=column_names)
#     return pd_results

# def create_scatterplot(data):
#     scatterplot = px.scatter(data, x = 'x', y = 'y', color = 'toolId')
#     return scatterplot

# #latest_df = update_DF()
# #print(latest_df)

# @app.callback(
#     Output('scatter-plot', 'figure'),
#     [Input('interval-component', 'n_intervals')]
# )
# def update_scatter_plot(n):
#     latest_data = update_DF()
#     fig = create_scatterplot(latest_data)
#     return fig

# if __name__ == '__main__':
#     app.run_server(debug=True,host = '127.0.0.1')