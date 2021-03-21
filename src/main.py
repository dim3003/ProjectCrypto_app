# coding=utf-8
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

import include.webscrapper as webs


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
        interval=1*10000,
        n_intervals=0
    ),
    dcc.Interval(
            id='interval-component',
            interval=1*10000, # in milliseconds
            n_intervals=0
        ),
    html.H2("Crypto project",className="m-2",style={'text-align':'center'}),

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
        dcc.Tab(label='Analysis', value='tab-2', children = html.Div([html.Div(id='analysis')])),
        dcc.Tab(label='Social',
                value='tab-3',
                children = html.Div([html.Div(id='dbLoader'),
                                    html.Div(id='social', children = [
                                        html.Div(id='initSocial',
                                                 children = dcc.RadioItems(
                                                        id='verifiedChoice',
                                                        value = 'allTweet')),
                                        html.Div(id='initGraph'), #graphs block
                                        html.Div([ #dropdown block
                                            dcc.Dropdown(
                                                id='tweetDropdown',
                                                options=[
                                                    {'label': 'Most recent tweets', 'value': 'mrtweet'},
                                                    {'label': 'Most positive tweets (last 24h)', 'value': 'mptweet'},
                                                    {'label': 'Most negative tweets (last 24h)', 'value': 'mntweet'}
                                                        ],
                                                value='mrtweet'
                                                    ),
                                            html.Div(id='tweetsList')])
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
@app.callback(Output('dbLoader', 'children'),
              Input('verifiedChoice', 'value'))
def loadDB(verif):
    ts.tweet_stream(verif) #creates the twitter live stream

import social

#Create a header with choices
@app.callback(Output('initSocial', 'children'),
              Input('sentiment_term', 'value'))
def loadHeader(crypto):
    return social.socialHeader(crypto)

#create graph content from social.py
@app.callback(Output('initGraph', 'children'),
              Input('social_interval', 'n_intervals'))
def update_content(num):
    content = social.socialGraph()
    return content


import analysisTab
@app.callback(Output('analysis', 'children'),
              [Input(component_id='sentiment_term', component_property='value'),
              Input('social_interval', 'n_intervals')])
def update_content_analysis_tab(sentiment_term,num):
    content = analysisTab.analysisPage(df = coindf[coindf['Name'] == sentiment_term]) #gets content from social.py
    return content
  
#Tweet dropdown
@app.callback(Output('tweetsList', 'children'),
              Input('tweetDropdown', 'value'))
def loadList(typeChoice):
    return social.socialDrop(typeChoice)


# Rendering Content
#######################
@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))

def render_content(tab):

    #Home tab
    ############

    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content Home'),
            #html.H4('Explanation of our Project'),
            #html.P('voici notre projet de advanced data analysis'),
            #html.P('etudiants en master de finance')


        ])

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
