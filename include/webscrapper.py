import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging
import sys
from time import sleep
#url pour tout avoir 
# A actualiser 1 fois par heure

logging.basicConfig(filename='scrapper.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def scrapCoin():
    try:
        url = "https://coinmarketcap.com/all/views/all/"
        req = requests.get(url)
        #print(req.text)
        soup = BeautifulSoup(req.text,'html.parser')
        table = soup.find("table")
        table_value = []
        #print(table.text)
        try:
            for value in soup.find_all('tr')[3:]:
                row_value = []
                row = value.find_all('td')
                #print(row[0].text)
                row_value.append(row[0].text) #Ranks
                row_value.append(row[1].text) #Name
                print(row[2].text)
                row_value.append(row[2].text) #Symbol
                row_value.append(row[3].text) #Market cap
                row_value.append(row[4].text) #Price
                row_value.append(row[5].text) #Circulating Supply
                row_value.append(row[6].text) #Volume (24h)
                row_value.append(row[7].text) #%1h
                row_value.append(row[8].text) #%24h
                row_value.append(row[9].text) #%7d
                table_value.append(row_value)
                
                logging.debug(f"=== Process {row[1].text} / Rank: {row[0].text}/ {len(soup.find_all('tr')[3:])} ===")
        except Exception as e:
            print(e)
            #print(f"=== Process {row[1].text} / Rank: {row[0].text}/ {len(soup.find_all('tr')[3:])} ===")
        columns = ["Ranks","Name","Symbol","Market Cap","Price","Circulating Supply","Volume(24h)","%1h","%24h","%7d"]
        df = pd.DataFrame(table_value,columns=columns)
        #print(len(table_value))
        df.index = df["Ranks"]
        df = df.iloc[:,1:]
        return df
    except Exception as e:
        #print(e)
        #print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
        logging.error(str(e))
  

if __name__ == "__main__":
    df = scrapCoin()
    #print(df.values)