import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings

from web3 import Web3

from logger import *
from util import *
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='base prediction sets reader')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xa0ee7a142d267c1f36714e4a8f75612f20a79720')
    parser.add_argument('--private_key', type=str, default='0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6')
    parser.add_argument('--market_names', type=str, nargs='+', default=['AMM1', 'AMM2', 'AMM3'])
    parser.add_argument('--alpha', type=str)
    parser.add_argument('--alphas', type=str, nargs='+')
    parser.add_argument('--beta', type=int)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)    
    args = parser.parse_args()

    # default parameters
    if args.beta is None:
        args.beta = len(args.market_names) // 2

    if args.alpha is not None:
        args.alphas = [float(args.alpha) / len(args.market_names) for _ in range(len(args.market_names))]

        
    print(args)

    
    ## setup logger
    os.makedirs(os.path.join(args.output_dir, args.exp_name), exist_ok=True)
    sys.stdout = Logger(os.path.join(args.output_dir, args.exp_name, 'out'))

        
        
    w3 = Web3(Web3.HTTPProvider(args.provider_url))
    assert(w3.isConnected())
    address = Web3.toChecksumAddress(args.address)
    nonce = w3.eth.getTransactionCount(address)
    market_contracts = get_market_contracts(w3.eth, args.market_names, args.output_dir)


    #TODO: only consider a DAI and ETH pair
    DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

    DAI = w3.eth.contract(DAI_addr, abi=open('script/abi_DAI.json').read())
    WETH = w3.eth.contract(WETH_addr, abi=open('script/abi_WETH.json').read())

    # init ACC
    acc_addr = json.loads(open(os.path.join(args.output_dir, f'acc.json')).read())['deployedTo']
    acc = w3.eth.contract(acc_addr, abi=open('out/ACC.sol/ACC.abi.json').read())
    # set sources
    for market_name in args.market_names:
        pair_addr = market_contracts[market_name]['factory'].functions.getPair(WETH_addr, DAI_addr).call()
        fun = acc.functions.addSource(pair_addr)
        tx = fun.buildTransaction({
            'from': address,
            'nonce': nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = w3.eth.account.signTransaction(tx, args.private_key)
        emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        nonce += 1

    # set beta
    fun = acc.functions.setBeta(args.beta)
    tx = fun.buildTransaction({
        'from': address,
        'nonce': nonce,
        'gas': 2000000, #TODO
        'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    })
    signed_tx = w3.eth.account.signTransaction(tx, args.private_key)
    emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    nonce += 1

    # set alphas for each market
    warnings.warn('alpha should be set by AMM itself')
    for market_name, alpha in zip(args.market_names, args.alphas):
        pair_addr = market_contracts[market_name]['factory'].functions.getPair(WETH_addr, DAI_addr).call()
        pair = w3.eth.contract(pair_addr, abi=open('out/IBasePS.sol/IBasePS.abi.json').read())
        fun = pair.functions.setAlpha(int(float(alpha)*10**18))
        tx = fun.buildTransaction({
            'from': address,
            'nonce': nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = w3.eth.account.signTransaction(tx, args.private_key)
        emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        nonce += 1
    
