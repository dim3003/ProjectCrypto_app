import  sqlite3
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly
import logging
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

from collections import deque
import dash_bootstrap_components as dbc

logging.basicConfig(filename='infos.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

conn = sqlite3.connect('twitter.db')
c = conn.cursor()

df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
df.sort_values('unix',inplace=True)
df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
df.dropna(inplace=True)





app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("It is our app !!!",className="m-2",style={'text-align':'center'}),
     dcc.Dropdown(
        id='sentiment_term',
        options=[
            {'label': 'Bitcoin', 'value': 'Bitcoin'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value='Bitcoin',
        className="mb-5"
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
            
           
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content Dashboard'),
            html.Div(className='row', children=[html.Div(dcc.Graph(id='live-graph', animate=True), className='col s12 m6 l6')]),
            #html.Div(className='row', children=[html.Div(id="recent-tweets-table", className='col s12 m6 l6')])
            # Ajout de l'interval
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content ML Model')
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
@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value'),
              Input(component_id='tabs-styled-with-props', component_property='value')],
              events=[State('graph-update', 'interval')])
def update_graph_scatter(sentiment_term,tab):
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

            data = plotly.graph_objs.Scatter(
                    x=X,
                    y=Y,
                    name='Scatter',
                    mode= 'lines+markers'
                    )

            return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                        yaxis=dict(range=[min(Y),max(Y)]),
                                                        title='Cryptocurrency: {}'.format(sentiment_term))}
        except Exception as e:
            logging.error(str(e))


# @app.callback(Output('recent-tweets-table', 'children'),
#               [Input(component_id='sentiment_term', component_property='value')])        
# def update_recent_tweets(sentiment_term):
#     try:
#         if sentiment_term:
#             df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 10", conn, params=(sentiment_term+'*',))
#         else:
#             df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 10", conn)

#         df['date'] = pd.to_datetime(df['unix'], unit='ms')

#         df = df.drop(['unix','id'], axis=1)
#         df = df[['date','tweet','sentiment']]

#         return generate_table(df, max_rows=10)
#     except Exception as e:
#         logging.error(str(e))

if __name__ == '__main__':
    app.run_server(debug=True)