# coding=utf-8
def tweet_stream(cryptos):
    import include.config
    from tweepy import Stream, OAuthHandler
    from tweepy.streaming import StreamListener
    import json
    import sqlite3
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from unidecode import unidecode
    import time
    import pandas as pd

    analyser = SentimentIntensityAnalyzer()

    #################
    # Database config
    #################

    #Drop the db if already existing one in the app
    conn = sqlite3.connect('./include/twitter.db')
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS sentiment")
    conn.commit()

    c.execute("CREATE TABLE IF NOT EXISTS sentiment (unix REAL, tweet TEXT, sentiment REAL, verified BOOLEAN)")
    conn.commit()


    c.execute("DELETE FROM sentiment")
    conn.commit()

    #Create a class to scrap stream of tweet
    class Listener(StreamListener):
        def on_data(self,data):
            try:

                data = json.loads(data)

                if 'limit' not in list(data.keys()):

                    tweet = unidecode(data['text'])

                    time_ms = data['timestamp_ms'] # à changer pour avoir directment les liens
                    vs = analyser.polarity_scores(tweet)
                    sentiment = vs['compound']
                    verified = data['user']['verified']
                    #print(time_ms,tweet,sentiment, verified)

                    #insert data in SQL database
                    if data['lang'] == 'en': #and data['retweet_count'] > 0
                        c.execute("INSERT INTO sentiment (unix, tweet, sentiment, verified) VALUES (?, ?, ?, ?)",(time_ms, tweet, sentiment, verified))
                        conn.commit()


            except  KeyError as e:
                print(str(e))
                time.sleep(1000)

            return True

        def on_error(self,status):
            print(status)

    def createStreamTwitter():
        while True:
            try:
                auth = OAuthHandler(include.config.consumer_key,include.config.consumer_secret)
                auth.set_access_token(include.config.access_token, include.config.access_token_secret)

                twitterStream = Stream(auth, Listener())
                twitterStream.filter(track = cryptos)
            except Exception as e:
                print(str(e))
                time.sleep(5)

    if __name__ == '__main__':
        createStreamTwitter()
    elif __name__ == 'include.tweet_stream':
        createStreamTwitter()
