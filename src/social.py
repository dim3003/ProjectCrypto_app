# coding=utf-8

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

def socialInit():

    #Db update_content
    ##################
    conn = sqlite3.connect('./include/twitter.db')
    c = conn.cursor()

    def create_table():
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        conn.commit()

    create_table()

    global df
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix',inplace=True)
    df['smoothed_sentiment'] = (df['sentiment'].rolling(int(len(df)/5)).mean() + 1) / 2
    df.dropna(inplace=True)

    # Index as date

    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    df.index = df['date']
    df.set_index('date', inplace=True)

    #last sentiment_term
    global lastSentiment
    if len(df['smoothed_sentiment']) > 0:
        lastSentiment = df['smoothed_sentiment'].iloc[-1]
    else:
        lastSentiment = 0


def socialHeader(crypto):

    headerBlock = html.Div([
                    html.H3(f'Twitter live sentiment of {crypto}'),
                    dcc.RadioItems(
                        id='verifiedChoice',
                        options=[
                            {'label': 'All tweets', 'value': 'allTweet'},
                            {'label': 'Verified author only', 'value': 'verifTweet'}
                        ],
                        value = 'allTweet',
                        labelStyle={'display': 'inline-block', 'padding':'1em'}
                    )],
                    style={'margin':'1em 1em 0 1em'})
    return headerBlock

def socialGraph():

    socialInit() #gets the data

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
                                    y=df['smoothed_sentiment']
                                )],

                                'layout': go.Layout(
                                    xaxis={'title': 'Time'},
                                    yaxis={'title': 'Sentiment'},
                                    margin={'l': 80, 'b': 40, 't': 10, 'r': 40},
                                    plot_bgcolor='#ececec',
                                    yaxis_range=[0,1])
                               }
                        ), style={'width':'60%', 'display':'inline-block'}),
                html.Div(
                    dcc.Graph(
                        id='twitterPie',
                        figure={
                            'data': [
                                go.Pie(
                                    marker = dict(colors=['1cbf1f', 'c1281f']),
                                    labels = ['Positive', 'Negative'],
                                    values = [lastSentiment, 1 - lastSentiment])
                                ],

                                'layout': go.Layout(
                                    margin={'l': 80, 'b': 40, 't': 90, 'r': 40})
                               }
                        ), style={'width':'30%', 'display':'inline-block'})
                ])

    return content


def socialDrop(typeChoice):
    socialInit()
    while len(df) <= 10:
        socialInit() #gets the data

    last = df.iloc[-10:, 1] #last 10 tweets from the db
    innerContent=[]
    for i in last:
        innerContent.append(html.Div(str(i)),)
        innerContent.append(html.Br(),)
    content=html.Div(innerContent, style={'padding':'2em'})

    return content
