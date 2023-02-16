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

class PSReader:
    def __init__(self, args):
        self.args = args

        ## setup logger
        os.makedirs(os.path.join(args.output_dir, args.exp_name), exist_ok=True)
        sys.stdout = Logger(os.path.join(args.output_dir, args.exp_name, 'out'))
        
        self.w3 = Web3(Web3.HTTPProvider(self.args.provider_url))
        assert(self.w3.isConnected())
        self.address = Web3.toChecksumAddress(self.args.address)
        # self.nonce = self.w3.eth.getTransactionCount(self.address)
        
        #TODO: assume that UniswapV2-style AMMs are used
        if 'AMM' in args.market_name:
            router02_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_router.json')).read())['deployedTo']
            factory_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_factory.json')).read())['deployedTo']
            self.router02 = self.w3.eth.contract(router02_addr, abi=open('out/IUniswapV2Router02.sol/IUniswapV2Router02.abi.json').read())
            self.factory = self.w3.eth.contract(factory_addr, abi=open('out/IUniswapV2Factory.sol/IUniswapV2Factory.abi.json').read())

        # elif args.market_name == 'AMM2':
        #     router02_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_router.json')).read())['deployedTo']
        #     factory_addr = json.loads(open(os.path.join(self.args.output_dir, f'{args.market_name.lower()}_factory.json')).read())['deployedTo']
        #     self.router02 = self.w3.eth.contract(router02_addr, abi=open('out/IUniswapV2Router02.sol/IUniswapV2Router02.abi.json').read())
        #     self.factory = self.w3.eth.contract(factory_addr, abi=open('out/IUniswapV2Factory.sol/IUniswapV2Factory.abi.json').read())

        else:
            raise NotImplementedError
        
        #TODO: only consider a DAI and ETH pair
        self.DAI_addr = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
        self.WETH_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

        self.DAI = self.w3.eth.contract(self.DAI_addr, abi=open('script/abi_DAI.json').read())
        self.WETH = self.w3.eth.contract(self.WETH_addr, abi=open('script/abi_WETH.json').read())


        
    # def check_ETH_balance(self):
    #     return self.w3.eth.get_balance(self.address)

    
    # def check_DAI_balance(self):
    #     return self.DAI.functions.balanceOf(self.address).call()

    
    # def check_WETH_balance(self):
    #     return self.WETH.functions.balanceOf(self.address).call()

    
    # def check_WETH_DAI_pair(self):
    #     pair_addr = self.factory.functions.getPair(self.WETH_addr, self.DAI_addr).call()
    #     pair = self.w3.eth.contract(pair_addr, abi=open('script/abi_uniswap_v2_pair.json').read())
    #     reserve0, reserve1, _ = pair.functions.getReserves().call()

    #     token0_addr = pair.functions.token0().call()
    #     token1_addr = pair.functions.token1().call()

    #     if token0_addr == self.WETH_addr and token1_addr == self.DAI_addr:
    #         DAI_ETH_price = reserve1 / reserve0
    #     else:
    #         assert(token1_addr == self.WETH_addr and token0_addr == self.DAI_addr)
    #         DAI_ETH_price = reserve0 / reserve1
            
    #     return DAI_ETH_price
    
        
    # # def buy_WETH(self, amount_in_wei):
    # #     swap_path = [self.WETH_addr, self.WETH_addr]

    # #     min_amount_out = int(self.uniswap_v2_router02.functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)
    # #     deadline = int(time.time() + 60) # TODO
    # #     fun = self.uniswap_v2_router02.functions.swapExactETHForTokens(
    # #         min_amount_out,
    # #         swap_path,
    # #         self.address,
    # #         deadline
    # #     )
        
    # #     tx = fun.buildTransaction({
    # #         'from': self.address,
    # #         'nonce': self.w3.eth.getTransactionCount(self.address),
    # #         'value': amount_in_wei,
    # #         'gas': 2000000, #TODO
    # #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    # #     })
    # #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    # #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # def swap_ETHforDAI_UniswapV2(self, amount_in_wei):

    #     warnings.warn('DBG')
    #     router02_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' # Uniswapv2
    #     router02 = self.w3.eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())

        
    #     # swap
    #     swap_path = [self.WETH_addr, self.DAI_addr]
    #     min_amount_out = int(router02.functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)
    #     deadline = int(time.time() + 60) # TODO
    #     fun = router02.functions.swapExactETHForTokens(
    #         min_amount_out,
    #         swap_path,
    #         self.address,
    #         deadline,
    #     )
        
    #     tx = fun.buildTransaction({
    #         'from': self.address,
    #         'nonce': self.nonce,
    #         'value': amount_in_wei,
    #         'gas': 2000000, #TODO
    #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    #     })
    #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    #     self.nonce += 1
        
    # def swap_ETHforDAI(self, amount_in_wei):

    #     # swap
    #     swap_path = [self.WETH_addr, self.DAI_addr]
    #     min_amount_out = int(self.router02.functions.getAmountsOut(amount_in_wei, swap_path).call()[1]*0.9)        
    #     deadline = int(time.time() + 60) # TODO
    #     fun = self.router02.functions.swapExactETHForTokens(
    #         min_amount_out,
    #         swap_path,
    #         self.address,
    #         deadline,
    #     )
        
    #     tx = fun.buildTransaction({
    #         'from': self.address,
    #         'nonce': self.nonce,
    #         'value': amount_in_wei,
    #         'gas': 2000000, #TODO
    #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    #     })
    #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    #     self.nonce += 1

        
    # def swap_DAIforETH(self, amount_in):

    #     # approve 
    #     tx = self.DAI.functions.approve(self.router02.address, amount_in).buildTransaction({
    #         'from': self.address, 
    #         'nonce': self.nonce,
    #         'gas': 2000000, #TODO
    #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    #     })
    #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    #     self.nonce += 1

    #     # swap
    #     swap_path = [self.DAI_addr, self.WETH_addr]
    #     min_amount_out = int(self.router02.functions.getAmountsOut(amount_in, swap_path).call()[1]*0.9)
    #     deadline = int(time.time() + 60) # TODO
    #     fun = self.router02.functions.swapExactTokensForETH(
    #         amount_in,
    #         min_amount_out, 
    #         swap_path,
    #         self.address,
    #         deadline,
    #     )
        
    #     tx = fun.buildTransaction({
    #         'from': self.address,
    #         'nonce': self.nonce,
    #         'gas': 2000000, #TODO
    #         'gasPrice': Web3.toWei('50', 'gwei'), #TODO
    #     })
    #     signed_tx = self.w3.eth.account.signTransaction(tx, self.args.private_key)
    #     emitted = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    #     self.nonce += 1

        
    def run(self):
        while True:

            pair_addr = self.factory.functions.getPair(self.WETH_addr, self.DAI_addr).call()
            pair = self.w3.eth.contract(pair_addr, abi=open('out/IBasePS.sol/IBasePS.abi.json').read())
            lower_interval, upper_interval = pair.functions.predict().call()
            lower_interval = lower_interval / 10**18
            upper_interval = upper_interval / 10**18
            threshold = pair.functions.getThreshold().call() / 10**18
            pred_obs_mean, pred_obs_var = pair.functions.getObsPrediction().call()
            pred_obs_mean, pred_obs_var = pred_obs_mean / 10**18, pred_obs_var / 10**18
            state_noise_var, obs_noise_var = pair.functions.getNoise().call()
            state_noise_var = state_noise_var / 10**18
            obs_noise_var = obs_noise_var / 10**18
            error = pair.functions.getMeanMiscoverage().call() / 10**18
            alpha = pair.functions.getAlpha().call() / 10**18

            print(f'[{args.market_name}, alpha = {alpha}] obs mean = {pred_obs_mean:.4f}, obs var = {pred_obs_var:.4f}, state noise var = {state_noise_var:.4f}, obs. noise var = {obs_noise_var:.4f}, '
                  f'threshold = {threshold:.4f}, price interval = ({lower_interval:.4f}, {upper_interval:.4f}), length = {upper_interval - lower_interval}, '
                  f'error = {error:.4f}'
            )
            time.sleep(self.args.time_interval_sec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='base prediction sets reader')
    parser.add_argument('--provider_url', type=str, default='http://127.0.0.1:8545')
    parser.add_argument('--address', type=str, default='0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266')
    parser.add_argument('--private_key', type=str, default='0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
    parser.add_argument('--market_name', type=str, choices=['AMM1', 'AMM2', 'AMM3'], default='AMM1')
    parser.add_argument('--time_interval_sec', type=int, default=0.01)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, required=True)
    
    args = parser.parse_args()

    reader = PSReader(args)
    reader.run()
