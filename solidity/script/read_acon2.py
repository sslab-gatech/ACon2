import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings
import pickle

import web3
from web3 import Web3

from logger import *
from util import *

class ACon2Reader:
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

        # init ACon2
        acon2_addr = json.loads(open(os.path.join(self.args.output_dir, f'acon2.json')).read())['deployedTo']
        self.acon2 = self.w3.eth.contract(acon2_addr, abi=open('out/ACon2.sol/ACon2.abi.json').read())

        
    def run(self):
        data = []
        data_fn = os.path.join(self.args.output_dir, self.args.exp_name, 'data.pk')
        gas_data_fn = os.path.join(self.args.output_dir, self.args.exp_name, 'gas_data.pk')

        os.makedirs(os.path.dirname(data_fn), exist_ok=True)
        n_err_cons = 0
        n_obs = 0
        gas_used_history = []
        
        while True:
            block_id = self.w3.eth.get_block_number()
            beta = self.acon2.functions.getBeta().call(block_identifier=block_id)
            n_sources = self.acon2.functions.getSources().call(block_identifier=block_id)

            gas_used_history.append(self.acon2.functions.eval().estimate_gas())
            lower_interval, upper_interval, lower_intervals, upper_intervals, observations = self.acon2.functions.eval().call(block_identifier=block_id)
            lower_interval = lower_interval / 10**18
            upper_interval = upper_interval / 10**18
            base_intervals = [[l / 10**18, u / 10**18] for l, u in zip(lower_intervals, upper_intervals)]
            
            prices = [float(v / 10**18) for v in observations]
            prices_str = ",".join([f'{v:.4f}' for v in prices])
            pseudo_label = np.median(prices)
            
            # compute errors
            n_obs += 1
            if not(pseudo_label >= lower_interval and pseudo_label <= upper_interval):
                n_err_cons += 1

            data.append({
                'prices': prices,
                'market_names': [k for k in self.market_contracts.keys()],
                'beta': beta,
                'n_sources': n_sources,
                'interval': [lower_interval, upper_interval],
                'miscoverage_cons': n_err_cons / n_obs,
            })

            # save gas history
            if len(gas_used_history) == 500:
                pickle.dump(gas_used_history, open(gas_data_fn, 'wb'))

            print(f'[ACon2] beta = {beta}, n_sources = {n_sources}, price = {prices_str}, pseudo-label= {pseudo_label:.4f}, '
                  f'price interval = ({lower_interval:.4f}, {upper_interval:.4f}), length = {upper_interval - lower_interval:.4f}, '
                  f'error_cons = {n_err_cons / n_obs:.4f}, '
                  f'gas used (for {len(gas_used_history)} TXs) = {np.mean(gas_used_history):.2f} +- {np.std(gas_used_history):.2f}'
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
    parser.add_argument('--time_interval_sec', type=int, default=0.01)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)

    args = parser.parse_args()
    print(args)

    reader = ACon2Reader(args)
    reader.run()
