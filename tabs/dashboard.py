import  sqlite3
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly
import logging
from dash.dependencies import Output, State, Input
import plotly.graph_objs as go

def update_graph_scatter(sentiment_term):
    if tab == 'tab-2':
        try:
            conn = sqlite3.connect('twitter.db')
            c = conn.cursor()
            df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + sentiment_term + '%',))
            df.sort_values('unix', inplace=True)
            df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()

            df['date'] = pd.to_datetime(df['unix'],unit='ms')
            print(df['date'])
            df.index = df['date']
            df.set_index('date', inplace=True)

            df = df.resample('1min').mean()

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
                                                        title='Term: {}'.format(sentiment_term))}
        except Exception as e:
            logging.error(str(e))