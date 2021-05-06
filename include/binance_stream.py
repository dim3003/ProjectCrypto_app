
#import tweet_stream
from binance.websockets import BinanceSocketManager
from binance.client import Client
import include.config
import websocket, json, pprint
from datetime import datetime
import pandas as pd
# lien pour ce connecter au server de binance pour avoir en temps réel les données
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

client = Client(include.config.api_key, include.config.api_secret, tld='us')
bm = BinanceSocketManager(client)


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    #print(message)
    #print('received message')
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']

    # True: seulement quand c'est la fin de la minute
    is_candle_closed = candle['x']
    close = candle['c']
    time = datetime.fromtimestamp(candle['t']/1000)
    n_trade = candle['n'] # number de trade
    #pprint.pprint(time)

    # condition pour s'assurer qu'une minute "pleine" c'est bien passé :)
    # sinon on va avoir ce qui se passe en cours de la minute + la fin
    if is_candle_closed:
        print("candle closed at {}".format(close))
        print(f'time: {time}')
        print(f'number of trades: {n_trade}')
        #logging.info("candle closed at {}".format(close))
        print("=====================")
        closes.append(float(close))
        if len(closes) > 1:
            return_crypto = ((closes[-1]/closes[-2])-1)*100
            #logging.info(f'Return: {return_crypto} %')
        print("closes")
        print(closes)

    

def livedata():        
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

def historicalData(symbol):
    # fetch 1 minute klines for the last day up until now
    try:
        klines = client.get_historical_klines(f"{symbol}USD", Client.KLINE_INTERVAL_1MINUTE, "3 day ago UTC") # timing à choisir soit en direct avec un websocket soit un appel API
    except Exception:
        klines = client.get_historical_klines(f"{symbol}BTC", Client.KLINE_INTERVAL_1MINUTE, "3 day ago UTC")
    columns = ['Date','Open','Close','High','Low','Volume','CloseTime','QuoteAssetVolume','NumberofTrade','TakerbuybaseV','TakerbuyquoteV','Ignore']
    df = pd.DataFrame(klines,columns=columns)
    df['Date'] = pd.to_datetime(df['Date']/1000,unit='s')
    df.index = df['Date']
    df = df.iloc[:,1:]
    df['Close'] = df['Close'].astype(float)
    df['NumberofTrade'] = df['NumberofTrade'].astype(int)
    return df

if __name__ == "__main__":
    df = historicalData()
