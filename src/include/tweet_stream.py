import include.config as config
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import time

analyser = SentimentIntensityAnalyzer()

# connect to my database
conn = sqlite3.connect('./twitter.db',check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
    conn.commit()

create_table()    


#Create a class to scrap stream of tweet 
class Listener(StreamListener):
    def on_data(self,data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms'] # à changer pour avori directment les liens
            vs = analyser.polarity_scores(tweet)
            sentiment = vs['compound']
            print(time_ms,tweet,sentiment)
            #insert data in SQL database
            #only english tweet
            if data['lang'] == 'en':
                c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",(time_ms, tweet, sentiment))
            conn.commit()
        except  KeyError as e:
            print(str(e))
        return True

    def on_error(self,status):
        print(status)

def createStreamTwitter():
    while True:
        try:
            auth = OAuthHandler(config.consumer_key,config.consumer_secret)
            auth.set_access_token(config.access_token, config.access_token_secret)

            twitterStream = Stream(auth, Listener())
            twitterStream.filter(track=["Bitcoin","Ethereum"])
        except Exception as e:
            print(str(e))
            time.sleep(5)

if __name__ == '__main__':
    createStreamTwitter()