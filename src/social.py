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

def social():
    return html.Div([
                dcc.Graph(
                    id='twitter',
                    figure={
                        'data': [
                            go.Scatter(
                                x=[1,3,4],
                                y=[3,6,12],
                            )],

                            'layout': go.Layout(
                                title="Twitter sentiment",
                                xaxis={'title': 'Time'},
                                yaxis={'title': 'Sentiment'},
                                margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                    }
                   )
                ])
