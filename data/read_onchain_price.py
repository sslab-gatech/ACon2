import os, sys
import subprocess
import json
from datetime import datetime, timedelta
import time
import numpy as np
from multiprocessing import Process, Manager
import pickle

def get_from_UniswapV2(pair0, pair1, time_start=None, time_end=None, time_step_sec=None):
    assert(pair0 == 'ETH')
    assert(pair1 == 'USD')
    assert(time_start)
    assert(time_end)
    assert(time_step_sec)

    url = 'https://api.thegraph.com/subgraphs/name/blocklytics/ethereum-blocks'
    url_UniswapV2 = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    n_jobs = 60
    
    data_pk = []
    data_dict_shared = Manager().dict()
    
    time_step_sec = timedelta(seconds=time_step_sec)
    time_curr = time_start

    def get_price(timestamp_req_list, data_dict):
        
        for i, timestamp_req in enumerate(timestamp_req_list, 1):
            # timestamp to block number
            query = '\'{"query": "{ blocks(first: 1, orderBy: timestamp, orderDirection: asc, where: {timestamp_gt: \\"%d\\",  timestamp_lt:\\"%d\\"}) {id number timestamp }}\"}\''%(
                timestamp_req, timestamp_req+500)
            result = os.popen(f'curl -s -X POST -H "Content-Type: application/json" -d {query} {url}').read()
            try:
                result = json.loads(result)
            except json.decoder.JSONDecodeError:
                continue
        
            blocks = result['data']['blocks']
            assert(len(blocks) == 1)
            block = blocks[0]

            blocknum = int(block['number'])
            timestamp = int(block['timestamp'])
            time_dt = np.array(timestamp, dtype='datetime64[s]')

            # get price    
            query_price = '\'{"query": "{ token(id: \\"0x6b175474e89094c44da98b954eedeac495271d0f\\", block: {number: %d}) { derivedETH } }"}\''%(blocknum) # read DAI
            result = os.popen(f'curl -s -X POST -H "Content-Type: application/json" -d {query_price} {url_UniswapV2}').read()
            try:
                result = json.loads(result)
            except json.decoder.JSONDecodeError:
                continue

            price = 1 / float(result['data']['token']['derivedETH'])

            print(f"[{i}/{len(timestamp_req_list)}] timestamp = {timestamp}, time = {time_dt}, block number = {blocknum}, price = {price}")
            data_dict[timestamp] = {'time': time_dt, 'price': price, 'block_number': blocknum}
        

    # multi-processing
    timestamp_list = []
    proc_list = []
    while time_curr <= time_end:
        timestamp_list.append(time_curr.timestamp())
        time_curr += time_step_sec
        
    timestamp_list_split = np.array_split(timestamp_list, n_jobs)

    for timestamp_list_i in timestamp_list_split:
        
        proc = Process(target=get_price, args=(timestamp_list_i, data_dict_shared))
        proc.start()
        proc_list.append(proc)
        
    for p in proc_list:
        p.join()

    # reformat data
    keys = sorted(data_dict_shared.keys())
    data_pk = [data_dict_shared[k] for k in keys]
    return data_pk
    
    
    # while time_curr <= time_end:

    #     # timestamp to block number
    #     timestamp_req = int(time_curr.timestamp())
    #     query = '\'{"query": "{ blocks(first: 1, orderBy: timestamp, orderDirection: asc, where: {timestamp_gt: \\"%d\\",  timestamp_lt:\\"%d\\"}) {id number timestamp }}\"}\''%(
    #         timestamp_req, timestamp_req+500)
    #     t_start = time.time()
    #     result = os.popen(f'curl -s -X POST -H "Content-Type: application/json" -d {query} {url}').read()
    #     print(time.time() - t_start)
    #     result = json.loads(result)
    #     blocks = result['data']['blocks']
    #     assert(len(blocks) == 1)
    #     block = blocks[0]
        
    #     blocknum = int(block['number'])
    #     timestamp = int(block['timestamp'])
    #     time_dt = np.array(timestamp, dtype='datetime64[s]')

    #     # get price    
    #     query_price = '\'{"query": "{ token(id: \\"0x6b175474e89094c44da98b954eedeac495271d0f\\", block: {number: %d}) { derivedETH } }"}\''%(blocknum) # read DAI
    #     t_start = time.time()

    #     result = os.popen(f'curl -s -X POST -H "Content-Type: application/json" -d {query_price} {url_UniswapV2}').read()
    #     print("uniswap =", time.time() - t_start)

    #     result = json.loads(result)

        
    #     price = 1 / float(result['data']['token']['derivedETH'])

    #     print(f"timestamp = {timestamp}, time = {time_dt}, block number = {blocknum}, price = {price}")
        
    #     # end
    #     time_curr += time_step_sec
    #     data_pk.append({'time': time_dt, 'price': price, 'block_number': blocknum})        
    #     #time.sleep(0.05)

    # return data_pk


if __name__ == '__main__':

    pair0 = 'ETH'
    pair1 = 'USD'
    root = f'price_{pair0}_{pair1}'

    time_start = datetime(2021, 1, 1, 0, 0, 0, 0)
    time_end = datetime(2021, 12, 31, 23, 59, 0, 0)
    time_step_sec = 60

    data = get_from_UniswapV2(pair0, pair1, time_start, time_end, time_step_sec)
    pickle.dump(data, open(os.path.join(root, 'UniswapV2.pk'), 'wb'))

    
    
    
