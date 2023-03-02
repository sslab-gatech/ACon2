"""
This is only demonstration purpose; we recommand to write a smart contract for efficient arbitrage.
"""

import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings
import itertools

import web3
import requests

from web3 import Web3

from logger import *
from util import *

class Arbitrageur:
    def __init__(self, args):
        self.args = args

        ## setup logger
        os.makedirs(os.path.join(args.output_dir, args.exp_name), exist_ok=True)
        sys.stdout = Logger(os.path.join(args.output_dir, args.exp_name, 'out'))
        sys.stderr = Logger(os.path.join(args.output_dir, args.exp_name, 'out_err'))
        
        self.w3 = Web3(Web3.HTTPProvider(self.args.provider_url))
        assert(self.w3.isConnected())
        self.address = Web3.toChecksumAddress(self.args.address)
        self.nonce = self.w3.eth.getTransactionCount(self.address) 
        self.markets = get_market_contracts(self.w3.eth, args.markets, self.args.output_dir)

        #TODO: only consider a DAI and ETH pair
        self.DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        self.WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

        self.DAI = self.w3.eth.contract(self.DAI_addr, abi=open('script/abi_DAI.json').read())
        self.WETH = self.w3.eth.contract(self.WETH_addr, abi=open('script/abi_WETH.json').read())


        # buy enough DAI
        self.swap_ETHforDAI_UniswapV2(int(100 * 1e18))

        # self.swap_ETHforDAI(self.markets[args.markets[0]], int(10 * 1e18)) #TODO

        np.random.seed(args.seed)

        
    def swap_ETHforDAI_UniswapV2(self, amount_in_wei):

        #TODO: generalize
        router02_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' # Uniswapv2
        router02 = self.w3.eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())

        
        # swap
        swap_path = [self.WETH_addr, self.DAI_addr]
        min_amount_out = int(router02.functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)
        deadline = int(time.time() + 60) # TODO
        fun = router02.functions.swapExactETHForTokens(
            min_amount_out,
            swap_path,
            self.address,
            deadline,
        )
        
        tx = fun.buildTransaction({
            'from': self.address,
            'nonce': self.nonce,
            'value': amount_in_wei,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
        
        
    def check_ETH_balance(self):
        return self.w3.eth.get_balance(self.address)

    
    def check_DAI_balance(self):
        return self.DAI.functions.balanceOf(self.address).call()

    
    def check_WETH_balance(self):
        return self.WETH.functions.balanceOf(self.address).call()

    
    def check_WETH_DAI_pair(self, market):
        pair_addr = market['factory'].functions.getPair(self.WETH_addr, self.DAI_addr).call()
        pair = self.w3.eth.contract(pair_addr, abi=open('script/abi_uniswap_v2_pair.json').read())
        reserve0, reserve1, _ = pair.functions.getReserves().call()

        token0_addr = pair.functions.token0().call()
        token1_addr = pair.functions.token1().call()

        if token0_addr == self.WETH_addr and token1_addr == self.DAI_addr:
            DAI_reserve = reserve1
            ETH_reserve = reserve0
        else:
            assert(token1_addr == self.WETH_addr and token0_addr == self.DAI_addr)
            DAI_reserve = reserve0
            ETH_reserve = reserve1
            
        DAI_ETH_price = DAI_reserve / ETH_reserve
            
        return DAI_ETH_price, DAI_reserve, ETH_reserve
    
        
    def swap_ETHforDAI(self, market, amount_in_wei, amount_in_dai=None):

        # swap
        swap_path = [self.WETH_addr, self.DAI_addr]
        deadline = int(time.time() + 60) # TODO

        if amount_in_wei is not None:
            assert(amount_in_dai is None)
            
            min_amount_out = int(market['router'].functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)
            fun = market['router'].functions.swapExactETHForTokens(
                min_amount_out,
                swap_path,
                self.address,
                deadline,
            )
            tx = fun.buildTransaction({
                'from': self.address,
                'nonce': self.nonce,
                'value': amount_in_wei,
                'gas': 2000000, #TODO
                'gasPrice': Web3.toWei('50', 'gwei'), #TODO
            })
        else:
            raise NotImplementedError
            # assert(amount_in_dai is not None)

            # min_amount_in = int(market['router02'].functions.getAmountsIn(amount_in_dai, swap_path).call()[1]*0.9)
            # fun = market['router02'].functions.swapETHForExactTokens(
            #     amount_in_dai,
            #     swap_path,
            #     self.address,
            #     deadline,
            # )
            # tx = fun.buildTransaction({
            #     'from': self.address,
            #     'nonce': self.w3.eth.getTransactionCount(self.address),
            #     'value': min_amount_in,
            #     'gas': 2000000, #TODO
            #     'gasPrice': Web3.toWei('50', 'gwei'), #TODO
            # })
            

            
            
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1

        
    def swap_DAIforETH(self, market, amount_in):

        # approve 
        tx = self.DAI.functions.approve(market['router'].address, amount_in).buildTransaction({
            'from': self.address, 
            'nonce': self.nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
        
        # swap
        swap_path = [self.DAI_addr, self.WETH_addr]
        min_amount_out = int(market['router'].functions.getAmountsOut(amount_in, swap_path).call()[1]*0.9)
        deadline = int(time.time() + 60) # TODO
        fun = market['router'].functions.swapExactTokensForETH(
            amount_in,
            min_amount_out, 
            swap_path,
            self.address,
            deadline,
        )
        
        tx = fun.buildTransaction({
            'from': self.address,
            'nonce': self.nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1


    # def arbitrage_naive(self, market_from, market_to, amount_dai):

    #     # print(amount_dai)
    #     swap_path = [self.WETH_addr, self.DAI_addr]
    #     amount_ETH = int(market_from['router'].functions.getAmountsIn(amount_dai, swap_path).call()[0])

    #     self.swap_ETHforDAI(market_from, amount_ETH)
    #     self.swap_DAIforETH(market_to, amount_dai)

        
    def arbitrage(self, market0_info, market1_info, min_diff):
        # token0: DAI, token1: ETH
        price0 = market0_info['token0'] / market0_info['token1']
        price1 = market1_info['token0'] / market1_info['token1']

        if abs(price0 - price1) < min_diff:
            return
        
        def opt(x1, y1, x2, y2): # assume 1:1
            return (x1*y2 - x2*y1) / (x1 + y1 + x2 + y2)

        if price0 > price1:
            market_info_from = market0_info
            market_info_to = market1_info
        else:
            market_info_from = market1_info
            market_info_to = market0_info
            
        c_opt = int(opt(market_info_from['token0'], market_info_from['token1'], market_info_to['token0'], market_info_to['token1']))
        amount_dai = c_opt
        if amount_dai <= 0:
            return
        swap_path = [self.WETH_addr, self.DAI_addr]
        amount_ETH = int(market_info_from['contract']['router'].functions.getAmountsOut(amount_dai, swap_path).call()[0])

        self.swap_ETHforDAI(market_info_from['contract'], amount_ETH)
        self.swap_DAIforETH(market_info_to['contract'], amount_dai)


    def run(self):
        while True:

            t_start = time.time()
            
            # price_diff_max = 0
            # for market_name0_i, market_name1_i in itertools.combinations(self.args.markets, 2):
            # for _ in range(1):
            market_name0_i, market_name1_i = np.random.choice(self.args.markets, 2, replace=False)

            try:
                # get current balance
                dai_price_market0_i, DAI_reserve0_i, ETH_reserve0_i = self.check_WETH_DAI_pair(self.markets[market_name0_i])
                dai_price_market1_i, DAI_reserve1_i, ETH_reserve1_i = self.check_WETH_DAI_pair(self.markets[market_name1_i])

                # price_diff_i = abs(dai_price_market0_i - dai_price_market1_i)
                # if price_diff_i > price_diff_max:
                market_name0, market_name1 = market_name0_i, market_name1_i
                dai_price_market0, DAI_reserve0, ETH_reserve0 = dai_price_market0_i, DAI_reserve0_i, ETH_reserve0_i
                dai_price_market1, DAI_reserve1, ETH_reserve1 = dai_price_market1_i, DAI_reserve1_i, ETH_reserve1_i
                # price_diff_max = price_diff_i

                self.arbitrage(
                    {'contract': self.markets[market_name0], 'token0': DAI_reserve0, 'token1': ETH_reserve0},
                    {'contract': self.markets[market_name1], 'token0': DAI_reserve1, 'token1': ETH_reserve1},
                    self.args.min_benefit_DAI
                )

                # dai_price_market0_after, _, _ = self.check_WETH_DAI_pair(self.markets[market_name0])
                # dai_price_market1_after, _, _ = self.check_WETH_DAI_pair(self.markets[market_name1])

                dai_price_market0_after = 0
                dai_price_market1_after = 0

            except web3.exceptions.ContractLogicError as e:
                print('transactions are likely reverted')
                print(e)
                continue
            except ValueError as e:
                print(e)
                continue
            # except requests.exceptions.ConnectionError as e:
            #     print(e)
            #     continue



            print(f'[arb: {self.args.address[:6]}, {time.time() - t_start:.2f} sec.] ETH balance = {self.w3.fromWei(self.check_ETH_balance(), "ether"): .4f} ether, '
                  f'DAI balance = {self.w3.fromWei(self.check_DAI_balance(), "ether"):.4f}, '
                  f'WETH balance = {self.check_WETH_balance()}, '
                  f'{market_name0} DAI / WETH price = {dai_price_market0:.4f} -> {dai_price_market0_after:.4f}, ',
                  f'{market_name1} DAI / WETH price = {dai_price_market1:.4f} -> {dai_price_market1_after:.4f}',
            )
            

            time.sleep(self.args.time_interval_sec)


            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arbitrageur client')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266')
    parser.add_argument('--private_key', type=str, default='0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    parser.add_argument('--markets', type=str, nargs='+', default=['UniswapV2', 'SushiSwap'])
    parser.add_argument('--time_interval_sec', type=int, default=0.0)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    #parser.add_argument('--min_benefit_WETH', type=int, default=1e10)
    #parser.add_argument('--min_benefit_DAI', type=int, default=0.0001)
    parser.add_argument('--min_benefit_DAI', type=int, default=1e-9)
    #parser.add_argument('--arb_amount_DAI', type=int, default=0.1*1e18)
    args = parser.parse_args()
    assert(len(args.markets) >= 2)
    print(args)
    arb = Arbitrageur(args)
    arb.run()
