# -> How to comment a block?
  
# Command + K + C


# -> How to uncomment a block?
  
# Command + K + U


from config import api_key, api_secret
from binance.client import Client
import csv
import pickle

client = Client(api_key, api_secret)

def obtain_cryptodata(Cryptoname):
    start_date = "1 Dec, 2012"
    end_date = "4 Feb, 2021"
    csvfile = open(f'dataset/data_{Cryptoname}.csv', 'w',newline='')
    candlestick_writer= csv.writer(csvfile, delimiter=',')

    # appel de Binance API pour avoir les données
    # 1er arg: pair de crypto => pour le moment c'est crypto /USDT
    candlesticks = client.get_historical_klines(f"{Cryptoname}USDT", Client.KLINE_INTERVAL_1HOUR, start_date, end_date)
    candlestick_writer.writerow(['Date','Open','Close','High','Low','Volumne','CloseTime','QuoteAssetVolume','NumberofTrade','TakerbuybaseV','TakerbuyquoteV','Ignore'])
    for i in range(len(candlesticks)):
        candlesticks[i][0] = candlesticks[i][0]/1000
        candlestick_writer.writerow(candlesticks[i])
        print("===================================")
        print(f'process value {i+1}/{len(candlesticks)}')

    csvfile.close()

if __name__ == '__main__':
    name = str(input("Which crypto: ")) #Ticker de la crypto
    obtain_cryptodata(name)