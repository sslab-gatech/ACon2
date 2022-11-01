import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings
import pickle

from web3 import Web3

from logger import *
from util import *

class ACCReader:
    def __init__(self, args):
        self.args = args

        ## setup logger
        os.makedirs(os.path.join(args.output_dir, args.exp_name), exist_ok=True)
        sys.stdout = Logger(os.path.join(args.output_dir, args.exp_name, 'out'))
        
        self.w3 = Web3(Web3.HTTPProvider(self.args.provider_url))
        assert(self.w3.isConnected())
        self.market_contracts = get_market_contracts(self.w3.eth, self.args.market_names, self.args.output_dir)
        self.DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        self.WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

        # init ACC
        acc_addr = json.loads(open(os.path.join(self.args.output_dir, f'acc.json')).read())['deployedTo']
        self.acc = self.w3.eth.contract(acc_addr, abi=open('out/ACC.sol/ACC.abi.json').read())

        
    def run(self):
        data = []
        data_fn = os.path.join(self.args.output_dir, self.args.exp_name, 'data.pk')
        os.makedirs(os.path.dirname(data_fn), exist_ok=True)
        n_err = 0
        n_obs = 0
        
        while True:
            beta = self.acc.functions.getBeta().call()
            n_sources = self.acc.functions.getSources().call()
            lower_interval, upper_interval = self.acc.functions.predict().call()
            lower_interval = lower_interval / 10**18
            upper_interval = upper_interval / 10**18

            name_prices = {
                name: check_WETH_DAI_pair(self.w3.eth, market, self.WETH_addr, self.DAI_addr)
                for name, market in self.market_contracts.items()}
            prices = [v for v in name_prices.values()]
            
            n_obs += 1
            if not(np.median(prices) >= lower_interval and np.median(prices) <= upper_interval):
                n_err += 1

            data.append({
                'prices': prices,
                'market_names': [k for k in name_prices.keys()],
                'beta': beta,
                'n_sources': n_sources,
                'interval': [lower_interval, upper_interval],
                'miscoverage': n_err / n_obs,
            })

            print(f'[ACC] beta = {beta}, n_sources = {n_sources}, median(price) = {np.median(prices):.4f}, '
                  f'price interval = ({lower_interval:.4f}, {upper_interval:.4f}), length = {upper_interval - lower_interval:.4f}, '
                  f'error = {n_err / n_obs:.4f}'
            )
            pickle.dump(data, open(data_fn, 'wb'))
            time.sleep(self.args.time_interval_sec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='base prediction sets reader')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xa0ee7a142d267c1f36714e4a8f75612f20a79720')
    parser.add_argument('--private_key', type=str, default='0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6')
    parser.add_argument('--market_names', type=str, nargs='+', default=['AMM1', 'AMM2', 'AMM3'])
    parser.add_argument('--beta', type=int, default=1)
    parser.add_argument('--time_interval_sec', type=int, default=0.1)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    
    args = parser.parse_args()

    reader = ACCReader(args)
    reader.run()