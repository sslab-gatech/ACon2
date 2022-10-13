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

class LP:
    def __init__(self, args):
        self.args = args

        ## setup logger
        os.makedirs(os.path.join(args.output_dir, args.exp_name), exist_ok=True)
        sys.stdout = Logger(os.path.join(args.output_dir, args.exp_name, 'out'))
        
        self.w3 = Web3(Web3.HTTPProvider(self.args.provider_url))
        assert(self.w3.isConnected())
        self.address = Web3.toChecksumAddress(self.args.address)
        self.nonce = self.w3.eth.getTransactionCount(self.address)
        self.market_contracts = get_market_contracts(self.w3.eth, [args.market_name], self.args.output_dir)
        self.market = self.market_contracts[args.market_name]

        # #TODO: assume that UniswapV2-style AMMs are used
        # if args.market_name == 'UniswapV2':
        #     router02_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
        #     factory_addr = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
        #     self.router02 = self.w3.eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())
        #     self.factory = self.w3.eth.contract(factory_addr, abi=open('script/abi_uniswap_v2_factory.json').read())

        # elif args.market_name == 'SushiSwap':
        #     router02_addr = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
        #     factory_addr = '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
        #     self.router02 = self.w3.eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())
        #     self.factory = self.w3.eth.contract(factory_addr, abi=open('script/abi_uniswap_v2_factory.json').read())
            
        # elif 'AMM' in args.market_name:
        #     router02_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_router.json')).read())['deployedTo']
        #     factory_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_factory.json')).read())['deployedTo']
        #     self.router02 = self.w3.eth.contract(router02_addr, abi=open('out/IUniswapV2Router02.sol/IUniswapV2Router02.abi.json').read())
        #     self.factory = self.w3.eth.contract(factory_addr, abi=open('out/IUniswapV2Factory.sol/IUniswapV2Factory.abi.json').read())

        # else:
        #     raise NotImplementedError
        
        print(f'[{self.args.market_name}] router address = {self.market["router"].address}, factory address = {self.market["factory"].address}')
        
        # #TODO: assume UniswapV2-style
        # router02_addr = json.loads(open(os.path.join(self.args.output_dir, 'amm1_router.json')).read())['deployedTo']
        # self.router02 = self.w3.eth.contract(router02_addr, abi=open('out/IUniswapV2Router02.sol/IUniswapV2Router02.abi.json').read())
        # factory_addr = json.loads(open(os.path.join(self.args.output_dir, 'amm1_factory.json')).read())['deployedTo']
        # self.factory = self.w3.eth.contract(factory_addr, abi=open('out/IUniswapV2Factory.sol/IUniswapV2Factory.abi.json').read())
        # print(f'[{self.args.market_name}] router02 address = {router02_addr}, factory address = {factory_addr}')

        
        
        #TODO: only consider a DAI and ETH pair
        self.DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        self.WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        self.DAI = self.w3.eth.contract(self.DAI_addr, abi=open('script/abi_DAI.json').read())
        self.WETH = self.w3.eth.contract(self.WETH_addr, abi=open('script/abi_WETH.json').read())

        # buy enough DAI
        self.swap_ETHforDAI_UniswapV2(int(100 * 1e18))
        
        
    def check_ETH_balance(self):
        return self.w3.eth.get_balance(self.address)

    
    def check_DAI_balance(self):
        return self.DAI.functions.balanceOf(self.address).call()

    
    def check_WETH_balance(self):
        return self.WETH.functions.balanceOf(self.address).call()

    
    def check_WETH_DAI_pair(self):

        pair_addr = self.market['factory'].functions.getPair(self.WETH_addr, self.DAI_addr).call()
        pair = self.w3.eth.contract(pair_addr, abi=open('out/IUniswapV2Pair.sol/IUniswapV2Pair.0.8.16.abi.json').read())
        reserve0, reserve1, _ = pair.functions.getReserves().call()

        token0_addr = pair.functions.token0().call()
        token1_addr = pair.functions.token1().call()

        if token0_addr == self.WETH_addr and token1_addr == self.DAI_addr:
            DAI_ETH_price = reserve1 / reserve0
        else:
            assert(token1_addr == self.WETH_addr and token0_addr == self.DAI_addr)
            DAI_ETH_price = reserve0 / reserve1
            
        return DAI_ETH_price
    
        
    # def buy_WETH(self, amount_in_wei):
    #     swap_path = [self.WETH_addr, self.WETH_addr]

    #     min_amount_out = int(self.uniswap_v2_router02.functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)
    #     deadline = int(time.time() + 60) # TODO
    #     fun = self.uniswap_v2_router02.functions.swapExactETHForTokens(
    #         min_amount_out,
    #         swap_path,
    #         self.address,
    #         deadline
    #     )
        
    #     tx = fun.buildTransaction({
    #         'from': self.address,
    #         'nonce': self.w3.eth.getTransactionCount(self.address),
    #         'value': amount_in_wei,
    #         'gas': 2000000, #TODO
    #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    #     })
    #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        
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
        
        
    def run(self):
        # get current balance
        print(f'[before] ETH balance = {self.w3.fromWei(self.check_ETH_balance(), "ether"): .4f} ether, '
              f'DAI balance = {self.check_DAI_balance()}, '
              f'WETH balance = {self.check_WETH_balance()}, '
        )
    

        # parameters
        ##TODO: use realistic values
        amountETHDesired = int(100*1e18)
        amountTokenDesired = int(100*1e18)
        amountTokenMin = int(amountTokenDesired*0.9)
        amountETHMin = int(amountETHDesired*0.9)

        # approve DAI
        tx = self.DAI.functions.approve(self.market['router'].address, amountTokenDesired).buildTransaction({
            'from': self.address, 
            'nonce': self.nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
        
        # approve WETH
        tx = self.WETH.functions.approve(self.market['router'].address, amountETHDesired).buildTransaction({
            'from': self.address, 
            'nonce': self.nonce,
            'gas': 2000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
        
        # fill ETH-DAI liquidity pool
        fun = self.market['router'].functions.addLiquidityETH(
            token=self.DAI_addr,
            amountTokenDesired=amountTokenDesired,
            amountTokenMin=amountTokenMin,
            amountETHMin=amountETHMin,
            to=self.address,
            deadline=int(time.time() + 60), # TODO,
        )
        
        tx = fun.buildTransaction({
            'from': self.address,
            'nonce': self.nonce,
            'value': amountETHDesired,
            'gas': 30000000, #TODO
            'gasPrice': Web3.toWei('50', 'gwei'), #TODO
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
        emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1

        
        # get current balance
        print(f'[after] ETH balance = {self.w3.fromWei(self.check_ETH_balance(), "ether"): .4f} ether, '
              f'DAI balance = {self.check_DAI_balance()}, '
              f'WETH balance = {self.check_WETH_balance()}, '
              f'[{self.args.market_name}] WETH / DIA price = {self.check_WETH_DAI_pair()}'
        )
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LP client')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xa0ee7a142d267c1f36714e4a8f75612f20a79720')
    parser.add_argument('--private_key', type=str, default='0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6')
    parser.add_argument('--market_name', type=str, default='AMM1')
    parser.add_argument('--pair0', type=str, choices=['ETH', 'DAI'], default='ETH')
    parser.add_argument('--pair1', type=str, choices=['ETH', 'DAI'], default='DAI')
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    
    args = parser.parse_args()

    lp = LP(args)
    lp.run()
