import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings
import random

from web3 import Web3

from logger import *
from util import *
from trader import Trader

class Adversary(Trader):
    def __init__(self, args):
        super().__init__(args)

        
    def run(self):
        time.sleep(self.args.initial_sleep_interval_sec)
        
        while True:
            # randomly choose a market
            market_name = np.random.choice(self.args.market_names)
            market_contracts = self.market_contracts[market_name]
            
            # get current balance
            price_prev = self.check_WETH_DAI_pair(market_contracts)
            
            
            # always sell ETH
            ETH_amount = int(10 * 1e18)
            self.swap_ETHforDAI(market_contracts, ETH_amount)

            print(f'[{market_name}] ETH balance = {self.w3.fromWei(self.check_ETH_balance(), "ether"): .4f} ether, '
                  f'DAI balance = {self.w3.fromWei(self.check_DAI_balance(), "ether"): .4f}, '
                  #f'WETH balance = {self.check_WETH_balance()}, '
                  f'{market_name} WETH / DAI previous price = {price_prev}, WETH / DAI price = {self.check_WETH_DAI_pair(market_contracts)}'
            )

            
            time.sleep(self.args.time_interval_sec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='trader client')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0x23618e81e3f5cdf7f54c3d65f7fbc0abf5b21e8f')
    parser.add_argument('--private_key', type=str, default='0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97')
    parser.add_argument('--market_names', type=str, nargs='+', default='UniswapV2')
    parser.add_argument('--initial_sleep_interval_sec', type=int, default=60.0)
    parser.add_argument('--time_interval_sec', type=int, default=10.0)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    args = parser.parse_args()

    adv = Adversary(args)
    adv.run()
