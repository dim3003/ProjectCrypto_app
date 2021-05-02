def loadTwint(sent, period):
    import pandas as pd
    import twint
    import datetime as dt
    import os
    import sqlite3
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()


    #create new directory
    if not os.path.isdir('tempTweets'):
        os.mkdir('tempTweets')


    def fetchTwint(period):
        c = twint.Config()

        c.Search = sent
        c.Custom["tweet"] = ["created_at", "tweet"]
        c.Verified = True
        c.Lang = "en"

        if period == 'daily':
            if sent == "Bitcoin": #add a min replies for bitcoin because otherwise too long to load
                c.Min_replies = 1 # min replies
            c.Since = (dt.datetime.today() - dt.timedelta(days = 1)).strftime('%Y-%m-%d')
            c.Output = f"tempTweets/dailyTweets{sent}.json"
        else:
            c.Min_replies = 10 # min replies for monthly
            c.Since = (dt.datetime.today() - dt.timedelta(days = 30)).strftime('%Y-%m-%d')
            c.Output = f"tempTweets/monthlyTweets{sent}.json"
        c.Hide_output = True
        c.Store_json = True

        tweets = twint.run.Search(c)

        #clean the json file

        def cleanData(period = 'daily'):
            df = pd.read_json(f"tempTweets/{period}Tweets{sent}.json", lines = True, orient = 'records')

            df['unix'] = df['created_at'].view('int64') // 10**6 #transform dates to unix
            df = df.drop('created_at', axis = 1)
            df['sentiment'] = df['tweet'].apply(lambda x: analyzer.polarity_scores(x)['compound']) #creates sentiment for each tweet
            df['verified'] = True

            df['tweet'] = df['tweet'].astype('string')
            df['unix'] = df['unix'].astype('string')

            df.to_json(f"tempTweets/{period}Tweets{sent}.json", lines = True, orient = 'records')


        if os.path.isfile(f"tempTweets/{period}Tweets{sent}.json"):
            if os.stat(f"tempTweets/{period}Tweets{sent}.json").st_size != 0:
                cleanData(period) #checks if file is not empty

    #look for tweets for the crypto
    if os.path.isfile(f"tempTweets/dailyTweets{sent}.json") == 0: #guard if already fetched daily
        fetchTwint('daily')
    if os.path.isfile(f"tempTweets/monthlyTweets{sent}.json") == 0: #guard if already fetched monthly
        fetchTwint('monthly')

    return 0
