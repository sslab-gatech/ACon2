import os, sys
from web3 import Web3

# import subprocess
import json
from datetime import datetime, timedelta
import time
import numpy as np
from multiprocessing import Process, Manager
import pickle


def find_block(w3, timestamp):
    print(timestamp)
    
    block = w3.eth.get_block('latest')
    print(block.timestmap)
    print(block.block_number)
    
    assert(timestamp < block.timestamp)
    # linear search
    while True:
        if timestamp >= block.timestamp:
            break

        block = w3.eth.get_block(block.block_number - 1)

    return block
            
    
def get_spot_price_UniswapV2(args, pair0, pair1, time_start, time_end, time_step_sec):
    w3 = web3.Web3(web3.Web3.HTTPProvider(args.provider_url))
    assert(w3.isConnected())

    block_start = find_block(w3, time_start.astype('datetime64[s]'))
    block_end = find_block(w3, time_end.astype('datetime64[s]'))

    sys.exit()
        
    
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='price reader')
    parser.add_argument('--provider_url', type=str, default='https://eth-mainnet.alchemyapi.io/v2/TeK8vT24gEP564FbC7Z2GPHQCOMDA8wb')
    # parser.add_argument('--address', type=str, default='0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266')
    # parser.add_argument('--private_key', type=str, default='0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    parser.add_argument('--market_name', type=str, default='UniswapV2')
    parser.add_argument('--pair0', type=str, default='INV')
    parser.add_argument('--pair1', type=str, default='ETH')
    parser.add_argument('--time_start', type=str, default='2022-01-01T00:00')
    parser.add_argument('--time_end', type=str, default='2022-07-31T23:59')
    parser.add_argument('--time_interval_sec', type=float, default=60)
    # parser.add_argument('--seed', type=int, default=None)
    # parser.add_argument('--output_dir', type=str, default='output')
    # parser.add_argument('--exp_name', type=str, required=True)
    args = parser.parse_args()

    # pair0 = 'ETH'
    # pair1 = 'USD'
    # time_start = datetime(2021, 1, 1, 0, 0, 0, 0)
    # time_end = datetime(2021, 12, 31, 23, 59, 0, 0)
    # time_step_sec = 60

    # #market = 'SushiSwap'
    # market = 'UniswapV2'
    # pair0 = 'INV'
    # pair1 = 'ETH'
    # time_start = datetime(2022, 1, 1, 0, 0, 0, 0)
    # time_end = datetime(2022, 7, 31, 23, 59, 0, 0)
    # time_step_sec = 60

    root = f'price_{pair0}_{pair1}_start_{str(time_start).replace(" ", "_")}_end_{str(time_end).replace(" ", "_")}_step_sec_{time_step_sec}'
    os.makedirs(root, exist_ok=True)

    if market == 'UniswapV2':
        data = get_spot_price_UniswapV2(args)
        pickle.dump(data, open(os.path.join(root, 'UniswapV2_spot_price.pk'), 'wb'))
        
    elif market == 'SushiSwap':
        raise NotImplementedError
        #data = get_from_exchange('https://api.thegraph.com/subgraphs/name/sushiswap/exchange', pair0, pair1, time_start, time_end, time_step_sec)
        pickle.dump(data, open(os.path.join(root, 'SushiSwap_spot_price.pk'), 'wb'))
        
        
    
    
