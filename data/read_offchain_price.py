import os, sys
import pandas as pd
#sfrom datetime import datetime, timedelta
import pickle
import time
import numpy as np

def sanity_check(data, time_start, time_end, time_step_sec):
    if time_start is None or time_end is None:
        return data
    t_start = data[0]['time']
    # assert(data[0]['time'] == time_start)
    # for i, d in enumerate(data):
    #     assert d['time'] == t_start + np.timedelta64(time_step_sec, 's')*i, f'time_obs ({d["time"]}) != time_exp ({t_start + np.timedelta64(time_step_sec, "s")*i})'
    # assert(data[-1]['time'] == time_end)
    for i in range(len(data)-1):
        assert data[i]['time'] != data[i+1]['time'], f"should hold {data[i]['time']} != {data[i+1]['time']}"
    
    return data

               
def get_from_coinbase(pair0, pair1, time_start=None, time_end=None, time_step_sec=None):
    import cbpro
    c = cbpro.PublicClient()

    def read_price_from_request(data_req):
        data = pd.DataFrame(data_req)
        data.columns= ["time","open","high","low","close","volume"]
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data.set_index('time', inplace=True)
        data.sort_values(by='time', ascending=True, inplace=True)

        data_req_ftr = []
        price = data['close']
        for i in range(len(data)):
            data_req_ftr.append({'time': data.index.values[i], 'price': price[i]})
        return data_req_ftr
    
    
    if (time_start is None) and (time_end is None):
        data_req = c.get_product_historic_rates(product_id=f'{pair0}-{pair1}')
        data_pk = read_price_from_request(data_req)
        
    
    elif (time_start is not None) and (time_end is not None):
        print('[coinbase] start time =', time_start, ', end time =', time_end)
        data_pk = []
        
        t_end = time_start
        f_end = False
        while not f_end:
            t_start = t_end
            t_end = t_start

            for _ in range(99): # do not request too much at once
                if t_end + np.timedelta64(time_step_sec, 's') > time_end:
                    f_end = True
                    break
                t_end += np.timedelta64(time_step_sec, 's')

            print(f'[coinbase, request] start time = {t_start}, end time = {t_end}')
            data_req_i = c.get_product_historic_rates(product_id=f'{pair0}-{pair1}', start=t_start, end=t_end, granularity=time_step_sec)
            data_pk_i = read_price_from_request(data_req_i)
            data_pk += data_pk_i
            t_end += np.timedelta64(time_step_sec, 's')

            time.sleep(0.05)

    else:
        raise NotImplementedError

    return sanity_check(data_pk, time_start, time_end, time_step_sec)

    
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
    #timestamp = client._get_earliest_valid_timestamp(f'{pair0}{pair1}T', '1h')
    data = client.get_historical_klines(f'{pair0}{pair1}T', '1m', limit=1000)
    data = pd.DataFrame(data,
                        columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'])
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data = data[['time','open','high','low','close','volume']]
    data.set_index('time', inplace=True)
    data.sort_values(by =['time'], inplace = True)
    return data
    
    
if __name__ == '__main__':
    pair0 = 'ETH'
    pair1 = 'USD'
    root = f'price_{pair0}_{pair1}'
    # time_start = datetime(2020, 1, 1, 0, 0, 0, 0)
    # #time_end = datetime(2020, 12, 31, 23, 59, 59, 0)
    # time_end = datetime(2020, 1, 1, 2, 0, 0, 0)
    time_start = np.datetime64('2020-01-01T00:00')
    #time_end = np.datetime64('2020-01-01T01:00')
    time_end = np.datetime64('2020-12-31T23:59')           

    time_step_sec = 60

    data = get_from_coinbase(pair0, pair1, time_start, time_end, time_step_sec)
    pickle.dump(data, open(os.path.join(root, 'coinbase.pk'), 'wb'))
    # print('gemini =\n', get_from_gemini(pair0, pair1))
    # print('kraken =\n', get_from_kraken(pair0, pair1))
    # print('binance =\n', get_from_binance(pair0, pair1))
    


