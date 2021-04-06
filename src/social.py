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
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL, verified BOOLEAN)")
        conn.commit()

    create_table()

    global df
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix',inplace=True)

    #smoothed sentiment value
    if len(df) < 5:
        df['smoothed_sentiment'] = df['sentiment']
    elif 5 < len(df) < 100: #takes all the db if its less than 100 to do the rolling mean otherwise takes half only
        df['smoothed_sentiment'] = (df['sentiment'].rolling(5).mean() + 1) / 2
    else:
        df['smoothed_sentiment'] = (df['sentiment'].rolling(100).mean() + 1) / 2

    # date column
    df['date'] = pd.to_datetime(df['unix'],unit='ms')

    return df


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

def socialGraph(verified):

    df = socialInit() #gets the data

    #Update Content
    ###############

    #filters the database if verified only is selected
    if verified == 'verifTweet':
        df = df[df.verified == True]

    #last sentiment_term
    lastSentiment = 0

    if len(df['smoothed_sentiment']) > 0:
        lastSentiment = df['smoothed_sentiment'].iloc[-1]


    content = html.Div([
                html.Div(
                    dcc.Graph(
                        id='twitter',
                        figure={ #Live graph figure line
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
                        figure={ #pie chart
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


def socialDrop(verified, typeChoice):
    df = socialInit()
    while len(df) <= 10:
        df = socialInit() #gets the data


    if verified == 'verifTweet':
        df = df[df.verified == True]


    #last 10 tweets from the db
    if len(df.iloc[:, 1]) < 10:
        last = df.iloc[:, 1]
    else:
        last = df.iloc[-10:, 1]

    #check if unique tweets

    ## compare all tweets & count number of double

    ## assert last to -(10 + number of double)

    ## remove  doubles from list with mode or smth

    #create the content
    innerContent=[]
    for i in last:
        innerContent.append(html.Div(str(i)),)
        innerContent.append(html.Br(),)
    content=html.Div(innerContent, style={'padding':'2em'})

    return content
