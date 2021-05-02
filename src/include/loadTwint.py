def loadTwint(sent):
    import pandas as pd
    import twint
    import datetime as dt
    import os
    import sqlite3
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()

    #Connect to db + create if not exists
    ##################
    conn = sqlite3.connect('./include/historicTwitter.db')
    cSQL = conn.cursor()
    cSQL.execute("DELETE FROM sentiment")
    conn.commit()


    #create new directory
    if not os.path.isdir('tempDailyTweets'):
        os.mkdir('tempDailyTweets')


    #look for tweets for the crypto
    if os.path.isfile(f"tempDailyTweets/dailyTweets{sent}.json") == 0:
        c = twint.Config()

        c.Search = sent
        c.Custom["tweet"] = ["created_at", "tweet"]
        c.Verified = True
        c.Lang = "en"
        if sent == "Bitcoin": #add a min replies for bitcoin because otherwise data overload
            c.Min_replies = 1 # min replies
        c.Output = f"tempDailyTweets/dailyTweets{sent}.json"
        c.Since = (dt.datetime.today() - dt.timedelta(days = 1)).strftime('%Y-%m-%d')
        c.Hide_output = True
        c.Store_json = True

        tweets = twint.run.Search(c)

        #clean the json file

        if os.path.isfile(f"tempDailyTweets/dailyTweets{sent}.json"):
            if os.stat(f"tempDailyTweets/dailyTweets{sent}.json").st_size != 0: #checks if file is not empty
                df = pd.read_json(f"tempDailyTweets/dailyTweets{sent}.json", lines = True, orient = 'records')

                df['unix'] = df['created_at'].view('int64') // 10**6 #transform dates to unix
                df = df.drop('created_at', axis = 1)
                df['sentiment'] = df['tweet'].apply(lambda x: analyzer.polarity_scores(x)['compound']) #creates sentiment for each tweet
                df['verified'] = True

                df['tweet'] = df['tweet'].astype('string')
                df['unix'] = df['unix'].astype('string')

                df.to_json(f"tempDailyTweets/dailyTweets{sent}.json", lines = True, orient = 'records')

    return 0
