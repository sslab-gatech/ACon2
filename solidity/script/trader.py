import os
import sys
import time
import numpy as np
import argparse
import time
import json
import warnings
import random
import pickle

import web3
from web3 import Web3

from logger import *
from util import *

class Trader:
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
        self.market_contracts = get_market_contracts(self.w3.eth, args.market_names, self.args.output_dir)
        
        #TODO: only consider a DAI and ETH pair
        self.DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        self.WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

        self.DAI = self.w3.eth.contract(self.DAI_addr, abi=open('script/abi_DAI.json').read())
        self.WETH = self.w3.eth.contract(self.WETH_addr, abi=open('script/abi_WETH.json').read())


        # buy enough DAI
        self.swap_ETHforDAI_UniswapV2(int(100 * 1e18))

        np.random.seed(args.seed)
        
        
        
    def check_ETH_balance(self):
        return self.w3.eth.get_balance(self.address)

    
    def check_DAI_balance(self):
        return self.DAI.functions.balanceOf(self.address).call()

    
    def check_WETH_balance(self):
        return self.WETH.functions.balanceOf(self.address).call()

    
    def check_WETH_DAI_pair(self, contracts):
        pair_addr = contracts['factory'].functions.getPair(self.WETH_addr, self.DAI_addr).call()
        pair = self.w3.eth.contract(pair_addr, abi=open('script/abi_uniswap_v2_pair.json').read())
        reserve0, reserve1, _ = pair.functions.getReserves().call()

        token0_addr = pair.functions.token0().call()
        token1_addr = pair.functions.token1().call()

        if token0_addr == self.WETH_addr and token1_addr == self.DAI_addr:
            DAI_ETH_price = reserve1 / reserve0
        else:
            assert(token1_addr == self.WETH_addr and token0_addr == self.DAI_addr)
            DAI_ETH_price = reserve0 / reserve1
            
        return DAI_ETH_price
    
        
    def swap_ETHforDAI_UniswapV2(self, amount_in_wei):

        warnings.warn('DBG')
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

        
    def swap_ETHforDAI(self, contracts, amount_in_wei):

        # swap
        swap_path = [self.WETH_addr, self.DAI_addr]
        min_amount_out = int(contracts['router'].functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)        
        deadline = int(time.time() + 60) # TODO
        fun = contracts['router'].functions.swapExactETHForTokens(
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
        gas_used_est = self.w3.eth.estimate_gas(tx)
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1

        return gas_used_est, min_amount_out
    
        
    def swap_DAIforETH(self, contracts, amount_in):

        # approve 
        tx = self.DAI.functions.approve(contracts['router'].address, amount_in).buildTransaction({
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
        min_amount_out = int(contracts['router'].functions.getAmountsOut(amount_in, swap_path).call()[1]*0.9)
        deadline = int(time.time() + 60) # TODO
        fun = contracts['router'].functions.swapExactTokensForETH(
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
        gas_used_est = self.w3.eth.estimate_gas(tx)
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
                    
        return gas_used_est, min_amount_out


        
    def run(self):
        gas_used_history = []
        gas_data_fn = os.path.join(self.args.output_dir, self.args.exp_name, 'gas_data.pk')

        while True:
            
            try:

                # randomly choose a market
                market_name = np.random.choice(self.args.market_names)
                market_contracts = self.market_contracts[market_name]

                # randomly sell or buy

                if np.random.rand() < 0.5:
                    # sell ETH
                    ETH_amount = int(np.random.uniform(0.1, 5) * 1e18)
                    gas_used, _ = self.swap_ETHforDAI(market_contracts, ETH_amount)
                    #print(f'[address = {self.address}] sell ETH = {self.w3.fromWei(ETH_amount, "ether"):.4f}')
                else:
                    # buy ETH
                    DAI_amount = int(np.random.uniform(0.1, 5) * 1e18)
                    gas_used, _ = self.swap_DAIforETH(market_contracts, DAI_amount)
                    #print(f'[address = {self.address}] sell DAI = {DAI_amount}')

                if gas_used is not None and len(gas_used_history) <= 600:
                    gas_used_history.append(gas_used)

                if len(gas_used_history) == 500:
                    pickle.dump(gas_used_history, open(gas_data_fn, 'wb'))


                # get current balance
                print(f'[trader] ETH balance = {self.w3.fromWei(self.check_ETH_balance(), "ether"): .4f} ether, '
                      f'DAI balance = {self.w3.fromWei(self.check_DAI_balance(), "ether"): .4f}, '
                      f'{market_name} WETH / DAI price = {self.check_WETH_DAI_pair(market_contracts)}, '
                      f'gas used (for {len(gas_used_history)} TXs) = {np.mean(gas_used_history):.4f} +- {np.std(gas_used_history):.4f}'
                )

            except web3.exceptions.ContractLogicError as e:
                print('transactions are likely reverted')
                print(e)
                continue
            except ValueError as e:
                print(e)
                continue

            time.sleep(self.args.time_interval_sec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='trader client')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266')
    parser.add_argument('--private_key', type=str, default='0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    parser.add_argument('--market_names', type=str, nargs='+', default='UniswapV2')
    parser.add_argument('--time_interval_sec', type=float, default=0.0)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    
    args = parser.parse_args()

    trader = Trader(args)
    trader.run()
