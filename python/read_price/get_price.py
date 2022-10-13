import os, sys
import pandas as pd

def get_from_coinbase(pair0, pair1):
    import cbpro

    c = cbpro.PublicClient()
    data = pd.DataFrame(c.get_product_historic_rates(product_id=f'{pair0}-{pair1}'))
    data.columns= ["time","open","high","low","close","volume"]
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)
    data.sort_values(by='time', ascending=True, inplace=True)
    
    return data

    
def get_from_gemini(pair0, pair1):
    import json, requests

    base_url = "https://api.gemini.com/v2"
    response = requests.get(base_url + f"/candles/{pair0.lower()}{pair1.lower()}/1m")
    data = pd.DataFrame(response.json(), columns =['time','open','high','low','close','volume'])
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data.set_index('time', inplace=True)
    data.sort_values(by =['time'], inplace = True)

    return data

def get_from_kraken(pair0, pair1):
    import krakenex
    from pykrakenapi import KrakenAPI
    api = krakenex.API()
    k = KrakenAPI(api)

    data = k.get_ohlc_data(f'{pair0}{pair1}', interval=1, ascending = True)[0]
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data = data[['time','open','high','low','close','volume']]
    data.set_index('time', inplace=True)
    data.sort_values(by =['time'], inplace = True)
    return data


def get_from_binance(pair0, pair1):
    from binance.client import Client
    api_key = 'Mbhd4omKdJ380wbasf84vGxrvhe5OqqmXxlDNbpu9WjEQGCMCL8kXYqFsbIh4xi4'
    api_secret = 'oyxsecLVBRQvnzbOGYSNiyzCgamG1d0VmUuV4iYm5D4CbB7evOQmN2dkNSHlhk8e'
    client = Client(api_key, api_secret)
    timestamp = client._get_earliest_valid_timestamp(f'{pair0}{pair1}T', '1h')
    data = client.get_historical_klines(f'{pair0}{pair1}T', '1m', limit=1000)
    data = pd.DataFrame(data,
                        columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'])
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data = data[['time','open','high','low','close','volume']]
    data.set_index('time', inplace=True)
    data.sort_values(by =['time'], inplace = True)
    return data
    
    
if __name__ == '__main__':
    pair0 = 'LINK'
    pair1 = 'USD'
    
    print('coinbase =\n', get_from_coinbase(pair0, pair1))
    print('gemini =\n', get_from_gemini(pair0, pair1))
    print('kraken =\n', get_from_kraken(pair0, pair1))
    print('binance =\n', get_from_binance(pair0, pair1))
    


