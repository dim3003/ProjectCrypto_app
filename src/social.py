# coding=utf-8

def socialInit():
    import dash_html_components as html
    import dash_core_components as dcc
    headerBlock = html.Div(
                    dcc.RadioItems(
                        id='verifiedChoice',
                        options=[
                            {'label': 'All tweets', 'value': 'allTweet'},
                            {'label': 'Verified', 'value': 'verifTweet'}
                        ],
                        value = 'allTweet',
                        labelStyle={'display': 'inline-block'}
                    ))
    return headerBlock

def socialGraph():
    #Import all packages
    ###############
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

    #Db update_content
    ##################

    conn = sqlite3.connect('./include/twitter.db')
    c = conn.cursor()

    def create_table():
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        conn.commit()

    create_table()

    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix',inplace=True)
    df['smoothed_sentiment'] = (df['sentiment'].rolling(int(len(df)/5)).mean() + 1) / 2
    df.dropna(inplace=True)

    # Index as date

    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    df.index = df['date']
    df.set_index('date', inplace=True)

    #last sentiment_term

    if len(df['smoothed_sentiment']) > 0:
        lastSentiment = df['smoothed_sentiment'].iloc[-1]
    else:
        lastSentiment = 0

    #Update Content
    ###############

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
                        ), style={'width':'60%', 'display':'inline-block'}),
                html.Div(
                    dcc.Graph(
                        id='twitterPie',
                        figure={
                            'data': [
                                go.Pie(
                                    labels = ['Positive', 'Negative'],
                                    values = [lastSentiment, 1 - lastSentiment]
                                    )
                                ],

                                'layout': go.Layout(
                                    title='Twitter live sentiment of Bitcoin',
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                               }
                        ), style={'width':'30%', 'display':'inline-block'})

                ])

    return content
