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

import base64

def card_person(name, img="image"):
    image_filename = 'IMG_5030.jpg' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    first_name, last_name = name.split(" ")[0].lower(), name.split(" ")[1].lower()
    last_name = last_name.replace('é','e')
    card_person = html.Div([
        html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),className='rounded-circle mx-auto d-block',height=200,width=100),className="m-2"),
        html.H3(name,className="text-center"),
        html.H5(f"{first_name}.{last_name}@unil.ch",className="text-center")
    ],className="justify-content-center")

    return card_person


def homePage():
    
    card_content_tech = [
    dbc.CardHeader(html.H3("Technical tab")),
    dbc.CardBody(
        [   
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
         ]
        ),
    ]

    card_content_social = [
    dbc.CardHeader(html.H3("Social tab")),
    dbc.CardBody(
        [   
            html.P('In this tab, we want to give our users the possibility to get an overview of all the latest Twitter posts referring to the selected cryptocurrency.'),
            html.P('In addition, we have implemented a sentiment analysis algorithm, which classifies each publication according to its positive or negative impact on the price.'),
            html.P('All of this is synthesized in a dynamic graph that is essential for any investment decision.'),
            
         ]
        ),
    ]
    image_filename = 'IMG_5030.jpg' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())

    # create a function
    card_persons = html.Div([
        html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),className='rounded-circle',height=200,width=400),className=""),
        html.H3("Guillaume Pavé",className="text-center"),
        html.H5("guillaume.pave@unil.ch",className="text-center")
    ],className="justify-content-center")

    return html.Div([
            html.H3('Welcome to our interface !',className="text-center mt-4"),
            # add images
            dbc.Row([
                html.Div([card_person(name='Dimitri André')],className="m-4"),
                html.Div([card_person("Guillaume Pavé")],className="m-4"),
                html.Div([card_person("Ruben Kempter")],className="m-4"),
            ],className="justify-content-center m-4"),
            
            html.H4('Explanation of our Project',className="text-center"),
            html.P('As part of a free project done during our master in Data science for Fiannce at the University of Lausanne, ',className="text-center"),
            html.P('we decided to propose an interface for anyone interested in the field of crypto currencies.',className="text-center"),
            html.P(120*'*',className="text-center"),
            html.P('We want to offer you a tool to make investment decisions with all cryptocurrencies available on the world main exchange : Binance.',className="text-center"),
            html.P('Our interface is subdivided into two main parts which are the following:',className="text-center"),
            dbc.Col(
             [
        dbc.Col(dbc.Card(card_content_tech, color="primary", outline=True),className="mb-4"),
        dbc.Col(dbc.Card(card_content_social, color="secondary", outline=True),className="mb-4"),
            ]),
            html.H2('Now it is time to ENJOY ! :D',className="text-center mb-4"),
        ])