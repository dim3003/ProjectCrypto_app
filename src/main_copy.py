import  sqlite3
import pandas as pd

from threading import Thread
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dtable
import plotly
import logging
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

import include.tweet_stream as ts
from collections import deque
import dash_bootstrap_components as dbc

logging.basicConfig(filename='infos.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('./twitter.db')
c = conn.cursor()

df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
df.sort_values('unix',inplace=True)
df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
df.dropna(inplace=True)



app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

card_content = [
    dbc.CardHeader("Card header"),
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text",
            ),
        ]
    ),
]

app.layout = html.Div([
    html.H2("It is our app !!!",className="m-2",style={'text-align':'center'}),
     dcc.Dropdown(
        id='sentiment_term',
        options=[
            {'label': 'Bitcoin', 'value': 'Bitcoin'},
            {'label': 'Ethereum', 'value': 'Ethereum'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='Bitcoin',
        className="mb-5"
    ),
    dcc.Interval(
            id='interval-component',
            interval=1*5000, # in milliseconds
            n_intervals=0
        ),
    html.H2("", className="m-2"),
    # NavBar ##
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1',children=[
        dcc.Tab(label='Home', value='tab-1'),
        dcc.Tab(label='Dashboard', value='tab-2'),
        dcc.Tab(label='Model', value='tab-3'),
        dcc.Tab(label='Data', value='tab-4')
    ], colors={
        "border": "white",
        "primary": "gold",
        "background": "cornsilk"
    }),
    html.Div(id='tabs-content-props')
])
#######################
## Usefull Functions ##
#######################

def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color':app_colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [

                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':app_colors['text'],
                                                'background-color':quick_color(d[2])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )



@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1'),
            html.H4('Explanation of our Project'),
            html.P('voici notre projet de advanced data analysis'),
            html.P('etudiants en master de Management')


        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content Dashboard'),
            html.Div(id='myChildren'),
            # Ajout de l'interval
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content ML Model'),
            html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="primary", inverse=True)),
                dbc.Col(
                    dbc.Card(card_content, color="secondary", inverse=True)
                ),
                dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="success", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="danger", inverse=True)),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(card_content, color="light")),
                dbc.Col(dbc.Card(card_content, color="dark", inverse=True)),
            ]
        ),
    ]
    )
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content Data')
        ])

###################
## Dashboard Tab ##
###################

# A mettre dans Un autre fichier pour être plus propre
# Ajouter le volume en dessous
@app.callback(Output('myChildren', 'children'),
              [Input(component_id='sentiment_term', component_property='value'),
              Input(component_id='tabs-styled-with-props', component_property='value'),
              Input('interval-component', 'n_intervals')],
              events=[State('graph-update', 'interval')])
def update_graph_scatter(sentiment_term,tab,n):
    if tab == 'tab-2':
        try:
            conn = sqlite3.connect('twitter.db')
            c = conn.cursor()
            df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + sentiment_term + '%',))
            df.sort_values('unix', inplace=True)
            df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()

            df['date'] = pd.to_datetime(df['unix'],unit='ms')

            df.index = df['date']
            df.set_index('date', inplace=True)

            # A ajouter quand il y aura la partie live

            #df = df.resample('1min').mean()

            df.dropna(inplace=True)

            X = df.index
            Y = df.sentiment_smoothed.values

            columns=[{'name': i,'id': i} for i in df.columns]

            figstock = go.Figure()

            figstock.add_trace(go.Scatter(x=X, y= Y,line=dict(color='blue', width=1.2), name = sentiment_term))
            figstock.update_layout(title_text= f'Stock Price of {sentiment_term}',yaxis_title=f'Polarity of Tweets about {sentiment_term}')

            child = html.Div([
                dcc.Graph(figure=figstock),
                #create a datable on Dash -> à ajuster le layout
                html.Div(className='row', children=[
                    html.Div(dtable.DataTable(
                                id='tableMonthly',
                                data=df.head(3).to_dict('records'), # number of tweets in datable
                                columns=columns,
                                style_cell={'textAlign': 'left',
                                'width': '40%'}),className='col s12 m6 l6')
                ]),

            ]
            )


            return child
        except Exception as e:
            logging.error(str(e))


if __name__ == '__main__':
    # A voir beug pour scrap en continue les tweets
    Thread(target=ts.createStreamTwitter).start()
    app.run_server(debug=True)
