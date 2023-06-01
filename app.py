#imports
import dash
from dash import Dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly.express as px
from collections import deque
import pandas as pd
import psycopg2
import time

#create dash app
app = dash.Dash(__name__)

#connect to the db containing our tag coordinates
conn = psycopg2.connect(
    host = "10.15.72.15",
    port = "5432",
    database = "postgres",
    user = "tooltracker",
    password = "crushingit"
)
#inside the app layout, setup a graph and also set up an interval so that you can update the scatterplot on a set interval
app.layout = html.Div([
    html.H1('Scatterplot'),
    dcc.Graph(
        id = 'scatter-plot'
    ),
    dcc.Interval(
        id='interval-component',
        interval=60*1000, #update scatterplot on a 60,000ms interval  
        n_intervals=0 #n_intervals is defined as the number of times the interval has passed, its default value is 0
    )
])

def update_DF(): #query the DB to get the latest x,y coordinates for each unique toolId
    cursor = conn.cursor()
    cursor.execute('SELECT public."toolLocation"."toolId", x, y FROM public."toolLocation" JOIN (SELECT "toolId", MAX("ts") AS latest_timestamp FROM public."toolLocation" GROUP BY "toolId") subquery ON public."toolLocation"."toolId" = subquery."toolId" AND public."toolLocation"."ts" = subquery.latest_timestamp ORDER BY public."toolLocation"."toolId" ASC') #order by timestamp descending order
    column_names = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    pd_results = pd.DataFrame(results, columns=column_names)
    return pd_results

def create_scatterplot(data): #use plotly express to make a scatterplot with collected data and use different colors for each toolId
    scatterplot = px.scatter(data, x = 'x', y = 'y', color = 'toolId', opacity = 0.1)
    return scatterplot

@app.callback( #the callback function updates the output when the input changes. We're trying to update the scatterplot whenever a 60s interval
               #has passed. Output and Input take a component_id and a component_property. The ID of our dcc.Interval is 'interval-component' and 
               #the property we're looking for changes in is the 'n_interval' component.
    Output('scatter-plot', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_scatter_plot(n): #this callback will use this function whenever the input values change, and pass the return into the output
    latest_data = update_DF()
    fig = create_scatterplot(latest_data)
    return fig

if __name__ == '__main__': #run the app
    app.run_server(debug=True,host = '127.0.0.1')