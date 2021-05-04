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
import os
import numpy as np
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

import include.tweet_stream as ts
from collections import deque
import dash_bootstrap_components as dbc

def socialInit(sent, period = 'daily'):

    #Db update_content
    ##################

    #create live db
    connLive = sqlite3.connect('./include/liveTwitter.db')
    cLive = connLive.cursor()

    dfL = pd.read_sql(f"SELECT * FROM sentiment WHERE tweet LIKE '%{sent}%' ORDER BY unix", connLive)
    connLive.commit()

    connLive = sqlite3.connect('./include/liveTwitter.db')

    #create historic db
    if period == 'daily':
        if os.path.isfile(f"tempTweets/dailyTweets{sent}.json"):
            if os.stat(f"tempTweets/dailyTweets{sent}.json").st_size != 0:
                dfH = pd.read_json(f"tempTweets/dailyTweets{sent}.json", lines = True, orient = 'records')
            else:
                return pd.DataFrame()
        else:
            return pd.DataFrame()
    else:
        if os.path.isfile(f"tempTweets/monthlyTweets{sent}.json"):
            if os.stat(f"tempTweets/monthlyTweets{sent}.json").st_size != 0:
                dfH = pd.read_json(f"tempTweets/monthlyTweets{sent}.json", lines = True, orient = 'records')
            else:
                return pd.DataFrame()
        else:
            return pd.DataFrame()



    #concatenate dataframes
    if len(dfH) > 0:
        df = pd.concat([dfL, dfH], sort=False)
    else:
        df = dfL

    #filters the database if verified only is selected
    #if verified == 'verifTweet':
    #    df = df[df.verified == True]

    #smoothed sentiment value
    if period == 'daily':
        if len(df) < 5:
            df['smoothed_sentiment'] = (df['sentiment'] + 1) / 2
        elif 5 <= len(df) < 100: #takes all the db if its less than 100 to do the rolling mean otherwise takes half only
            df['smoothed_sentiment'] = (df['sentiment'].rolling(5).mean() + 1) / 2
        elif 100 <= len(df) < 1000: #takes all the db if its less than 100 to do the rolling mean otherwise takes half only
            df['smoothed_sentiment'] = (df['sentiment'].rolling(50).mean() + 1) / 2
        else:
            df['smoothed_sentiment'] = (df['sentiment'].rolling(100).mean() + 1) / 2
    else:
        df['smoothed_sentiment'] = (df['sentiment'].rolling(50).mean() + 1) / 2


    # date column
    df['date'] = pd.to_datetime(df['unix'], unit = 'ms')
    if 'date' in df.columns:
        df.sort_values('date', inplace=True)

    df = df.dropna()

    return df


def socialHeader(crypto):
    headerBlock = html.Div([
                    html.H3(f'Twitter live sentiment of {crypto}'),
                    ],
                    style={'margin':'1em 1em 0 1em'})

    return headerBlock

def socialGraph(sent, period):
    df = socialInit(sent, period) #gets the data

    #Update Content
    ###############

    #last sentiment_term
    lastSentiment = 0

    if  5 >= len(df) >= 1:
        lastSentiment = df['smoothed_sentiment'].iloc[-1] #if smoothed sentiment is on 1 last
    elif 5 < len(df) < 100:
        lastSentiment = df['smoothed_sentiment'].iloc[-5] #if smoothed sentiment is on 5 last
    elif 100 <= len(df):
        lastSentiment = df['smoothed_sentiment'].iloc[-100] #if smoothed sentiment is on 100 last$

    if len(df) > 0:
        content = html.Div([
                    html.Div(
                        dcc.Graph(
                            id='twitter',
                            figure={ #Live graph figure line
                                'data': [
                                    go.Scatter(
                                        x=df['date'],
                                        y=df['smoothed_sentiment'] #takes only smoothed sentiment with values

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
    else:
        content = html.Div("LOADING GRAPHS ...", style={'padding': '10em', 'display':'inline-block'})

        if period == 'monthly':
            content = html.Div("LOADING MONTHLY GRAPHS ... this could take a minute ...", style={'padding': '10em', 'display':'inline-block'})


    return content


def socialDrop(typeChoice, sent):

    df = socialInit(sent)

    #if no content
    content = html.Div('Loading tweets...', style={'padding':'5em'})

    if len(df) != 0:
        #last 10 tweets from the db
        tweets = df.iloc[:10, 1]

        if len(df.iloc[:, 1]) > 15: #do some checks if we have enough tweets

            if typeChoice == 'mptweet':
                df.sort_values(by = ['sentiment'], inplace = True)
                tweets = df.iloc[-10:, 1]
            elif typeChoice == 'mntweet':
                df.sort_values(by = ['sentiment'], ascending = False, inplace = True)
                tweets = df.iloc[-10:, 1]
            else:
                tweets = df.iloc[-10:, 1]
            #check if unique tweets
            i = 1
            while len(pd.unique(tweets)) < 10:
                tweets = pd.unique(df.iloc[-(10 + i):, 1])
                i+=1

        #create the content
        innerContent=[]
        for i in tweets:
            innerContent.append(html.Div(str(i)),)
            innerContent.append(html.Br(),)
        content=html.Div(innerContent, style={'padding':'2em'})

    return content
