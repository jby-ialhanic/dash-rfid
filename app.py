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
import random

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
        interval=5*1000, #update scatterplot on a 60,000ms interval  
        n_intervals=0 #n_intervals is defined as the number of times the interval has passed, its default value is 0
    )
])

#functions

def random_noise(list):
    return_list = [] #define an empty array
    for element in list: #cycle through all entries in your original array
        plusminus = random.randrange(0,2) #this will be used to decide if you're going to subract or add the simulated noise
        ran_var = random.randrange(0,5) #random noise generation
        ran_var = ran_var/10
        if plusminus == 0:
            element = element + ran_var #add
        else:
            element = element - ran_var #subtract
        return_list.append(element) #store values into empty array
    return return_list #return the array

def update_DF(): #query the DB to get the latest x,y coordinates for each unique toolId
    cursor = conn.cursor()
    cursor.execute('SELECT public."toolLocation"."toolId", x, y FROM public."toolLocation" JOIN (SELECT "toolId", MAX("ts") AS latest_timestamp FROM public."toolLocation" GROUP BY "toolId") subquery ON public."toolLocation"."toolId" = subquery."toolId" AND public."toolLocation"."ts" = subquery.latest_timestamp ORDER BY public."toolLocation"."toolId" ASC') #order by timestamp descending order
    column_names = [desc[0] for desc in cursor.description] #define the title of each column
    results = cursor.fetchall() #fetch data from postgres db
    pd_results = pd.DataFrame(results, columns=column_names) #create a pandas dataframe with the data you received from postgres db
    ynoise = random_noise(pd_results["y"]) #generate noise for y axis values
    xnoise = random_noise(pd_results["x"]) #generate noise for x axis values
    pd_results["y"] = ynoise #overwrite your dataframe
    pd_results["x"] = xnoise
    return pd_results #return results

def create_scatterplot(data): #use plotly express to make a scatterplot with collected data and use different colors for each toolId
    scatterplot = px.scatter(data, x = 'x', y = 'y', color = 'toolId', opacity = 0.8)
    return scatterplot

@app.callback( #the callback function updates the output when the input changes. We're trying to update the scatterplot whenever a 60s interval
               #has passed. Output and Input take a component_id and a component_property. The ID of our dcc.Interval is 'interval-component' and 
               #the property we're looking for changes in is the 'n_interval' component.
    Output('scatter-plot', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('scatter-plot', 'figure')]
)
def update_scatter_plot(n, existing_fig): #this callback will use this function whenever the input values change, and pass the return into the output
    # print("update 1")
    latest_data = update_DF()
    fig = create_scatterplot(latest_data)
    if n == 0:
        return fig
    else:
        print(latest_data['x'][0])
        for i in range(4):
          existing_fig['data'][i]['x'][0] = latest_data['x'][i]
          existing_fig['data'][i]['y'][0] = latest_data['y'][i] 
        # existing_fig['data'][0]['x'][0] = existing_fig['data'][0]['x'][0] + 10.0
        # existing_fig['data'][0]['y'][0] = existing_fig['data'][0]['y'][0] + 10.0
        # existing_fig.add_trace(fig)
        return existing_fig
        # existing_fig.add_trace(latest_data)

if __name__ == '__main__': #run the app
    app.run_server(debug=True,host = '127.0.0.1')