# coding=utf-8
def tweet_stream(verif):
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

    conn = sqlite3.connect('./include/twitter.db')
    c = conn.cursor()

    def create_table():
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL, verified BOOLEAN)")
        conn.commit()

    create_table()

    c.execute("DELETE FROM sentiment")
    conn.commit()


    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%bitcoin%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix',inplace=True)

    if len(df) < 100: #takes all the db if its less than 100 to do the rolling mean otherwise takes half only
        df['smoothed_sentiment'] = (df['sentiment'].rolling(int(len(df))).mean() + 1) / 2
    else:
        df['smoothed_sentiment'] = (df['sentiment'].rolling(100).mean() + 1) / 2
    df.dropna(inplace=True)

    # Index as date

    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    df.index = df['date']
    df.set_index('date', inplace=True)



    #Create a class to scrap stream of tweet
    class Listener(StreamListener):
        def on_data(self,data):
            try:
                print(verif)
                if verif == 398120:
                    print('delete db from change of verif')
                    c.execute("DELETE FROM sentiment")
                    conn.commit()

                data = json.loads(data)
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
            return True

        def on_error(self,status):
            print(status)

    def createStreamTwitter():
        while True:
            try:
                auth = OAuthHandler(include.config.consumer_key,include.config.consumer_secret)
                auth.set_access_token(include.config.access_token, include.config.access_token_secret)

                twitterStream = Stream(auth, Listener())
                twitterStream.filter(track=["Bitcoin"])
            except Exception as e:
                print(str(e))
                time.sleep(5)

    if __name__ == '__main__':
        createStreamTwitter()
    elif __name__ == 'include.tweet_stream':
        createStreamTwitter()
