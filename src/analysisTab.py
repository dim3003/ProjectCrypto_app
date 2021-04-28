import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dtable
import plotly
import logging
import random
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import include.tweet_stream as ts
from collections import deque
import dash_bootstrap_components as dbc
import include.binance_stream as bs

import plotly.figure_factory as ff

def analysisPage(df=None):
    #print(name)
    name = df['Name'].values[0]
    df = bs.historicalData(df['Symbol'].values[0])
    content = html.Div([
        html.Div([html.Div(
                    dcc.Graph(
                        id='graphPrice',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=df.index,
                                    y=df['Close'],
                                )],

                                'layout': go.Layout(
                                    title=f'Close price of {name}',
                                    yaxis={'title': 'Price ($)'},
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                               }
                        ), style={'width':'100%', 'display':'block'}),
                html.Div(
                    dcc.Graph(
                        id='graphStat',
                        figure={
                            'data': [
                                go.Bar(
                                    x=df.index,
                                    y=df['NumberofTrade']
                                )],

                                'layout': go.Layout(
                                    height= 200,
                                     xaxis={'title': 'Time'},
                                    yaxis={'title': 'Number of trade'},
                                    margin={'l': 80, 'b': 40, 't': 10, 'r': 40})
                               }
                        ), style={'width':'100%', 'height':'10%', 'display':'block'})
                        ],style={'width':'60%', 'display':'inline-block'}),
                html.Div([html.Div(
                    dcc.Graph(
                        figure={
                            'data': [
                                go.Box(
                                    x=df['Close'].pct_change().dropna(),
                                    showlegend=False,
                                    notched=True,
                                    name=f""
                                )],

                                'layout': go.Layout(
                                    title=f'Box Plot of {name} Returns (1min)',
                                    xaxis={'title': 'Return'},
                                    yaxis={'title':''},
                                    height= 300,
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 30})
                               }
                        ), style={'width':'100%', 'height':'10%', 'display':'block'}),
                html.Div(
                    dcc.Graph( 
                        figure={
                            'data': [
                                go.Histogram(
                                    x=df['Close'].pct_change().dropna(),
                                )],

                                'layout': go.Layout(
                                    title=f'Distribution of {name} Returns (1min)',
                                    xaxis={'title': 'Returns'},
                                    yaxis={'title': 'Count'},
                                    height= 300,
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 30})
                               }
                        ), style={'width':'100%', 'height':'10%', 'display':'block'})
                        ],style={'width':'30%', 'display':'inline-block'}),

                ])
    
    return content