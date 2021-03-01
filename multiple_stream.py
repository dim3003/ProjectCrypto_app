#use my tweet+stream script
import tweet_stream
from binance.websockets import BinanceSocketManager
from binance.client import Client
import config

client = Client(config.api_key, config.api_secret, tld='us')
bm = BinanceSocketManager(client)

def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something
# start any sockets here, i.e a trade socket
conn_key = bm.start_trade_socket('BNBBTC', process_message)
# then start the socket manager
bm.start()
tweet_stream.createStreamTwitter()