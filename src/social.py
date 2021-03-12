import  sqlite3
import pandas as pd

from threading import Thread
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dtable
import plotly
import logging
import random
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

import include.tweet_stream as ts
from collections import deque
import dash_bootstrap_components as dbc

#Getting twitter data
#####################
conn = sqlite3.connect('./twitter.db')
c = conn.cursor()

df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
df.sort_values('unix', inplace=True) # Sort by unix time
# Cuts data into 5 parts and does the mean of the last part:
df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
df.dropna(inplace=True)

#Create date index
df['date'] = pd.to_datetime(df['unix'],unit='ms')

df.index = df['date']
df.set_index('date', inplace=True)


#Assign X and Y for twitter sentiment
X = df.index
Y = df.smoothed_sentiment.values

#Social function to be returned
################################

def social():
    return html.Div([
                dcc.Graph(
                    id='twitter',
                    figure={
                        'data': [
                            go.Scatter(
                                x=X,
                                y=Y,
                            )],

                            'layout': go.Layout(
                                title="Twitter sentiment",
                                xaxis={'title': 'Time'},
                                yaxis={'title': 'Sentiment'},
                                margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                    }
                   )
                ])
