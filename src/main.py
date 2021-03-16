# coding=utf-8
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

########
#HOME##
#######

logging.basicConfig(filename='infos.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#################
# Database config
#################

conn = sqlite3.connect('./twitter.db')
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

# App creation with BOOTSTRAP
#############################

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    html.H2("Crypto project",className="m-2",style={'text-align':'center'}),

    #Dropdown to choose Crypto
     dcc.Dropdown(
        id='sentiment_term',
        options=[ #options des valeurs du dropdown
            {'label': 'Bitcoin', 'value': 'Bitcoin'},
            {'label': 'Ethereum', 'value': 'Ethereum'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='Bitcoin',
        className="mb-5"
    ),
    html.H2("", className="m-2"),
    # NavBar ##
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1',children=[
        dcc.Tab(label='Home', value='tab-1'),
        dcc.Tab(label='Analysis', value='tab-2'),
        dcc.Tab(label='Social', value='tab-3'),
    ], colors={
        "border": "white",
        "primary": "gold",
        "background": "cornsilk"
    }),
    html.Div(id='tabs-content-props')
])

# app.callback => permet de faire changer les valeurs selon les actions de l'utilisateurs (https://dash.plotly.com/basic-callbacks)
@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))

def render_content(tab):

    #Home tab
    ############

    if tab == 'tab-1':
        return html.Div([
            html.H3('Welcome to our interface !'),
            html.H4('Explanation of our Project'),
            html.P('As part of a free project done during our master in Data science for Fiannce at the University of Lausanne, '),
            html.P('we decided to propose an interface for anyone interested in the field of crypto currencies.'),
            html.P(120*'*'),
            html.P('We want to offer you a tool to make investment decisions with all cryptocurrencies available on the wold main exchange : Binance.'),
            html.P('Our interface is subdivided into two main parts which are the following:'),
            html.H5('Technical tabs:'),
            html.P('In this part, you will first find a filter in order to select the crypto currency of your choice. '),
            html.P('You will then find the major indicators such as its price, the different volumes exchanged in the form of graphs, constantly updated to the second.'),
            html.P('In addition, we allow you to have a clear and synthetic visualization of the following elements:'),
            html.P('- Rank by market cap'),
            html.P('- Market capitalization '),
            html.P('- All time high'),
            html.P('- Circulating supply'),
            html.P('- Moving average'),
            html.P('- MACD '),
            html.P('- ADX'),
            html.P('- RSI'),
            html.P('- OBV'),
            html.P(120*'*'),
            html.H5('Social Tab:'),
            html.P('In this tab, we want to give our users the possibility to get an overview of all the latest Reddit and Tweeter posts referring to the selected cryptocurrency.'),
            html.P('In addition, we have implemented a sentiment analysis algorithm, which classifies each publication according to its positive or negative impact on the price.'),
            html.P('All of this is synthesized in a dynamic graph that is essential for any investment decision.'),
            html.H4('Now it is time to ENJOY ! :D'),









        ])

    #Technicals tab
    ############

    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content Analysis'),
            html.Div(id='myChildren'),
            # Ajout de l'interval
        ])

    #Social tab
    ############

    elif tab == 'tab-3':
        import social

        return social.social()

if __name__ == '__main__':

    app.run_server(debug=True)


