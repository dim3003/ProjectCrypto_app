import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
#url pour tout avoir 
# A actualiser 1 fois par heure
def scrapCoin():
  url = "https://coinmarketcap.com/all/views/all/"
  req = requests.get(url)

  soup = BeautifulSoup(req.text,'html.parser')



  table = soup.find("table")
  table_value = []
  for value in soup.find_all('tr')[3:]:
    row_value = []
    row = value.find_all('td')
    row_value.append(row[0].text)
    row_value.append(row[1].text)
    row_value.append(row[2].text)
    row_value.append(row[3].text)
    row_value.append(row[4].text)
    row_value.append(row[5].text)
    row_value.append(row[6].text)
    row_value.append(row[7].text)
    row_value.append(row[8].text)
    row_value.append(row[9].text)
    table_value.append(row_value)
    #mettre dans un logo file :)
    print(f"=== Process {row[1].text} / Rank: {row[0].text}/ {len(soup.find_all('tr')[3:])} ===")
  columns = ["Ranks","Name","Symbol","Market Cap","Price","Circulating Supply","Volume(24h)","%1h","%24h","%7d"]
  df = pd.DataFrame(table_value,columns=columns)
  df.index = df["Ranks"]
  df = df.iloc[:,1:]
  return df

if __name__ == "__main__":
    df = scrapCoin()
    print(df)