def loadTwint(cryptos):
    import pandas as pd
    import twint
    import datetime as dt
    import os
    import shutil
    import sqlite3
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()

    #Connect to db + create if not exists
    ##################
    conn = sqlite3.connect('./include/twitter.db')
    cSQL = conn.cursor()


    cSQL.execute("DELETE FROM sentiment")
    conn.commit()

    cSQL.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL, verified BOOLEAN)")
    conn.commit()

    #create new directory
    if not os.path.isdir('tempDailyTweets'):
        os.mkdir('tempDailyTweets')


    #look for tweets for each crypto
    for i in cryptos[:3]:

        c = twint.Config()

        c.Search = i
        c.Custom["tweet"] = ["created_at", "tweet"]
        c.Verified = True
        c.Lang = "en"
        c.Min_replies = 1 # min replies
        c.Output = f"tempDailyTweets/dailyTweets.json"
        c.Since = (dt.datetime.today() - dt.timedelta(1)).strftime('%Y-%m-%d') 
        c.Until = dt.datetime.today().strftime('%Y-%m-%d')
        c.Hide_output = True
        c.Store_json = True

        tweets = twint.run.Search(c)

        df = pd.read_json("tempDailyTweets/dailyTweets.json", lines = True, orient = 'records')

        df['unix'] = df['created_at'].view('int64') // 10**6 #transform dates to unix
        df = df.drop('created_at', axis = 1)
        df['sentiment'] = df['tweet'].apply(lambda x: analyzer.polarity_scores(x)['compound']) #creates sentiment for each tweet
        df['verified'] = True

        df['tweet'] = df['tweet'].astype('string')
        df['unix'] = df['unix'].astype('string')


        df = df.dropna()

        if len(df) > 0:
            df.to_sql('sentiment', con = conn, if_exists = 'append', index = False)


        df = df.iloc[0:0] #empty the dataframe



    #destroys the temp files
    shutil.rmtree('tempDailyTweets')

    return ""
