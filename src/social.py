# coding=utf-8

def social():
    import  sqlite3
    import pandas as pd

    import threading
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

    #################
    # Database config
    #################
    conn = sqlite3.connect('./include/twitter.db')
    c = conn.cursor()

    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix',inplace=True)
    df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
    df.dropna(inplace=True)

    # Index as date
    ###############

    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    df.index = df['date']
    df.set_index('date', inplace=True)

    content = html.Div([
                html.Div(
                    dcc.Graph(
                        id='twitter',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=df.index,
                                    y=df['smoothed_sentiment'],
                                )],

                                'layout': go.Layout(
                                    title='Twitter live sentiment of Bitcoin',
                                    xaxis={'title': 'Time'},
                                    yaxis={'title': 'Sentiment'},
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                               }
                        ))
                ])

    return content
