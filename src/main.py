# coding=utf-8
import  sqlite3
import pandas as pd

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dtable
import plotly
import logging
import random
import os
import shutil
import numpy as np
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

from collections import deque
import dash_bootstrap_components as dbc

# Our librairies #
import include.webscrapper as webs
import include.tweet_stream as ts
import include.loadTwint as loadTwint

# Our Pages #
import social
import analysisTab
from homepage import homePage

# Initialize log file #
logging.basicConfig(filename='infos.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# App creation with BOOTSTRAP
#############################

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

global coindf
coindf = webs.scrapCoin()

options = []

for name in coindf['Name'].values:
    options.append({'label':name,'value':name})


app.layout = html.Div([
    dcc.Interval(
        id='social_interval',
        disabled=False,
        interval=1*4000,
        n_intervals=0
    ),
    dcc.Interval(
        id='social_drop_interval',
        disabled=False,
        interval=1*15000,
        n_intervals=0
    ),
    dcc.Interval(
            id='interval-component',
            interval=1*30000, # in milliseconds => 30000 miliseconds = 30secs
            n_intervals=0
        ),
    html.H2(dbc.Card(html.H2("The analysis of Crypto",className="m-2"), color="primary", outline=True),className="m-4",style={'text-align':'center'}),

    #Dropdown to choose Crypto
     dcc.Dropdown(
        id='sentiment_term',
        options=options,
        value='Bitcoin',
        className="mb-5"
    ),
    html.H2("", className="m-2"),
    # NavBar ##
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1',children=[
        dcc.Tab(label='Home', value='tab-1'),
        dcc.Tab(label='Analysis', value='tab-2', children = html.Div([html.Div(id='analysis'),
        html.Div(id='cryptoStat')])),
        dcc.Tab(label='Social',
                value='tab-3',
                children = html.Div([html.Div(id='social',
                                              children = [html.Div(id = 'dbDaily'),
                                                          html.Div(id = 'dbLoader'),
                                                          html.Div(id='initSocial',
                                                                   children = [html.Div(id = "headerSocial"),
                                                                               dcc.Dropdown(id='tweetPeriod',
                                                                                            options=[{'label': 'Daily tweets', 'value': 'daily'},
                                                                                                    {'label': 'Monthly tweets', 'value': 'monthly'},
                                                                                                    ],
                                                                                            value = 'daily'),
                                                                              html.Div(id='initGraph'), #graphs block
                                                                              html.Div([ #dropdown block
                                                                              dcc.Dropdown(id='tweetDropdown',
                                                                                           options=[{'label': 'Most recent tweets', 'value': 'mrtweet'},
                                                                                                   {'label': 'Most positive tweets (last 24h)', 'value': 'mptweet'},
                                                                                                   {'label': 'Most negative tweets (last 24h)', 'value': 'mntweet'}
                                                                                                   ],
                                                                                           value='mrtweet'),
                                                                              html.Div(id='tweetsList')])#close dropdown bloc
                                                                              ]#closes children list
                                                                 )#close initSocial
                                    ]) #close id social div children
                        ])) #close dcc.Tab social + Tabs + Dropdown

    ], colors={
        "border": "white",
        "primary": "gold",
        "background": "cornsilk"
    }),
    html.Div(id='tabs-content-props')
])

#Load social tab content
########################

cryptos = list(coindf['Name'].values) #get all cryptos names

################
## Social Tab ##
################

# Database config
#################

#Drop the db if already existing one in the app
connLive = sqlite3.connect('./include/liveTwitter.db')
cLive = connLive.cursor()

cLive.execute("CREATE TABLE IF NOT EXISTS sentiment (unix REAL, tweet TEXT, sentiment REAL, verified BOOLEAN)")
connLive.commit()

cLive.execute("DELETE FROM sentiment")
connLive.commit()

#remove daily tweets if dir exists
if os.path.isdir('tempTweets'):
    shutil.rmtree('tempTweets')

#Callbacks for content

@app.callback(Output('dbDaily', 'children'),
              [Input('sentiment_term', 'value'),
              Input('tweetPeriod', 'value')]
              )
def loadHistoric(sent, period):
    loadTwint.loadTwint(sent, period) #creates twitter daily tweets


@app.callback(Output('dbLoader', 'children'),
              Input('dbLoader', 'children'))
def tweetStream(dummy):
    ts.tweet_stream(cryptos) #creates the twitter live stream


#Create a header with choices
@app.callback(Output('headerSocial', 'children'),
              Input('sentiment_term', 'value'))
def loadHeader(crypto):
    return social.socialHeader(crypto)

#create graph content from social.py
@app.callback(Output('initGraph', 'children'),
              [Input('sentiment_term', 'value'),
               Input('tweetPeriod', 'value'),
               Input('social_interval', 'n_intervals')])
def update_content(sent, period, num):
    content = social.socialGraph(sent, period)
    return content

#Tweet dropdown
@app.callback(Output('tweetsList', 'children'),
             [Input('tweetDropdown', 'value'),
              Input('sentiment_term', 'value'),
              Input('social_drop_interval', 'n_intervals')])
def loadList(typeChoice, sent, num):
    return social.socialDrop(typeChoice, sent)


##################
## Analysis Tab ##
##################

@app.callback(Output('analysis', 'children'),
              [Input(component_id='sentiment_term', component_property='value'),
              Input('interval-component', 'n_intervals')])
def update_content_analysis_tab(sentiment_term,num):
    content = analysisTab.analysisPage(df = coindf[coindf['Name'] == sentiment_term]) #gets content from social.py
    return content

def defineCard(title,text):
    card_content = [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.P(
                    text,
                    className="card-text",
                ),
            ]
        ),
    ]

    return card_content


@app.callback(Output('cryptoStat','children'),
            Input(component_id='sentiment_term', component_property='value'))
def update_content_stat_crypto(sentiment_term):
    df = coindf[coindf['Name'] == sentiment_term]
    row_1 = dbc.Row(
    [
        dbc.Col(dbc.Card(defineCard("Rank",df.index), color="primary", outline=True)),
        dbc.Col(dbc.Card(defineCard("Symbol",df['Symbol']), color="secondary", outline=True)),
        dbc.Col(dbc.Card(defineCard("Market Cap",df['Market Cap']), color="info", outline=True)),
    ],
    className="m-4",
    )

    row_2 = dbc.Row(
        [
            dbc.Col(dbc.Card(defineCard("Price",df['Price']), color="success", outline=True)),
            dbc.Col(dbc.Card(defineCard("Circulating supply",df['Circulating Supply']), color="warning", outline=True)),
            dbc.Col(dbc.Card(defineCard("Volumne (24h)",df['Volume(24h)']), color="danger", outline=True)),
        ],
        className="m-4",
    )

    row_3 = dbc.Row(
        [
            dbc.Col(dbc.Card(defineCard("%change (1h)",df["%1h"]), color="primary", outline=True)),
            dbc.Col(dbc.Card(defineCard("%change (24h)",df["%24h"]), color="secondary", outline=True)),
            dbc.Col(dbc.Card(defineCard("%change (7d)",df["%7d"]), color="info", outline=True)),
        ],
        className="m-4",
    )
    cards = html.Div([row_1, row_2,row_3])

    return cards


# Rendering Content
#######################
@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))

def render_content(tab):

    #Home tab
    ############

    if tab == 'tab-1':
        return homePage()

    #Technicals tab
    ############

    elif tab == 'tab-2':
        pass

    #Social tab
    ############
    elif tab == 'tab-3':
        pass



#Run the app if it is main
if __name__ == '__main__':

    app.run_server(debug=True)
