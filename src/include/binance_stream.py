# créer une table pour binance close

#import tweet_stream
from binance.websockets import BinanceSocketManager
from binance.client import Client
import config
import websocket, json, pprint
from datetime import datetime

# lien pour ce connecter au server de binance pour avoir en temps réel les données
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

client = Client(config.api_key, config.api_secret, tld='us')
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

    

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()