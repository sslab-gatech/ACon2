import os, sys
import web3 
import argparse

# import subprocess
import json
from datetime import datetime, timedelta
import time
import numpy as np
from multiprocessing import Process, Manager
import pickle

def find_block(w3, timestamp):

    block_start = w3.eth.get_block('earliest')
    block_end = w3.eth.get_block('latest')    

    assert(block_end.number != block_start.number)
    assert block_start.timestamp < timestamp < block_end.timestamp, f'{block_start.timestamp} < {timestamp} < {block_end.timestamp}'
    
    # binary search
    while True:
        block_number_mid = (block_start.number + block_end.number) // 2
        block_mid = w3.eth.get_block(block_number_mid)

        # print(block_start.timestamp, block_end.timestamp, timestamp)
        
        if timestamp < block_mid.timestamp:
            block_end = block_mid
        else:
            block_start = block_mid
        
        if block_end.number - block_start.number <= 1:
            block_final = block_end
            break

    return block_final


def get_price(w3, factory, block_number, token0_addr, token1_addr):
    pair_addr = factory.functions.getPair(token0_addr, token1_addr).call(block_identifier=block_number)
    pair = w3.eth.contract(pair_addr, abi=open('abi/abi_uniswap_v2_pair.json').read())
    reserve0, reserve1, _ = pair.functions.getReserves().call(block_identifier=block_number)

    token0_addr_pair = pair.functions.token0().call(block_identifier=block_number)
    token1_addr_pair = pair.functions.token1().call(block_identifier=block_number)

    if token0_addr_pair == token0_addr and token1_addr_pair == token1_addr:
        price = reserve1 / reserve0
    else:
        assert(token1_addr_pair == token0_addr and token0_addr_pair == token1_addr)
        price = reserve0 / reserve1

    return price


def tokenname2addr(token_name):
    if token_name == 'INV':
        return '0x41D5D79431A913C4aE7d69a668ecdfE5fF9DFB68'
    elif token_name == 'WETH':
        return '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    elif token_name == 'DAI':
        return '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    else:
        raise NotImplementedError


def get_spot_price_UniswapV2(args):
    w3 = web3.Web3(web3.Web3.HTTPProvider(args.provider_url))
    assert(w3.isConnected())

    # find blocks
    block_start = find_block(w3, np.datetime64(args.time_start, 's').astype('uint'))
    block_end = find_block(w3, np.datetime64(args.time_end, 's').astype('uint'))
    print(f"block start time = {np.array(block_start.timestamp, dtype='datetime64[s]')}, block end time = {np.array(block_end.timestamp, dtype='datetime64[s]')}")

    # UniswapV2 factory
    factory_addr = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    factory = w3.eth.contract(factory_addr, abi=open('abi/abi_uniswap_v2_factory.json').read())

    # read price
    for block_number in range(block_start.number, block_end.number+1):
        t = time.time()
        price = get_price(w3, factory, block_number, token0_addr=tokenname2addr(args.token0), token1_addr=tokenname2addr(args.token1))
        print(f'[running time = {time.time() - t}] price = {price}')
    
    sys.exit()
        
    
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='price reader')
    #parser.add_argument('--provider_url', type=str, default='https://eth-mainnet.alchemyapi.io/v2/TeK8vT24gEP564FbC7Z2GPHQCOMDA8wb')
    parser.add_argument('--provider_url', type=str, default='https://weirdwolf.gtisc.gatech.edu:8545')

    # parser.add_argument('--address', type=str, default='0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266')
    # parser.add_argument('--private_key', type=str, default='0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    parser.add_argument('--market_name', type=str, default='UniswapV2')
    parser.add_argument('--token0', type=str, default='WETH')
    parser.add_argument('--token1', type=str, default='INV')
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

    root = f'price_{args.token0}_{args.token1}_start_{str(args.time_start).replace(" ", "_")}_end_{str(args.time_end).replace(" ", "_")}_step_sec_{args.time_interval_sec}'
    os.makedirs(root, exist_ok=True)

    if args.market_name == 'UniswapV2':
        data = get_spot_price_UniswapV2(args)
        pickle.dump(data, open(os.path.join(root, 'UniswapV2_spot_price.pk'), 'wb'))
        
    elif market == 'SushiSwap':
        raise NotImplementedError
        #data = get_from_exchange('https://api.thegraph.com/subgraphs/name/sushiswap/exchange', pair0, pair1, time_start, time_end, time_step_sec)
        pickle.dump(data, open(os.path.join(root, 'SushiSwap_spot_price.pk'), 'wb'))
        
        
    
    
