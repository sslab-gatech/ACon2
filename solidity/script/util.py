import os, sys
import json
import web3

def get_market_contracts(w3eth, market_names, output_dir):
    market_contracts = {}
    for market_name in market_names:
    
        if market_name == 'UniswapV2':
            router02_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
            factory_addr = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
            router02 = w3eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())
            factory = w3eth.contract(factory_addr, abi=open('script/abi_uniswap_v2_factory.json').read())

        elif market_name == 'SushiSwap':
            router02_addr = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
            factory_addr = '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
            router02 = w3eth.contract(router02_addr, abi=open('script/abi_uniswap_v2_router02.json').read())
            factory = w3eth.contract(factory_addr, abi=open('script/abi_uniswap_v2_factory.json').read())

        elif 'AMM' in market_name:
            router02_addr = json.loads(open(os.path.join(output_dir, f'{market_name.lower()}_router.json')).read())['deployedTo']
            factory_addr = json.loads(open(os.path.join(output_dir, f'{market_name.lower()}_factory.json')).read())['deployedTo']
            router02 = w3eth.contract(router02_addr, abi=open('out/IUniswapV2Router02.sol/IUniswapV2Router02.abi.json').read())
            factory = w3eth.contract(factory_addr, abi=open('out/IUniswapV2Factory.sol/IUniswapV2Factory.abi.json').read())

        else:
            raise NotImplementedError

        market_contracts[market_name] = {'factory': factory, 'router': router02}
        
    return market_contracts



def check_WETH_DAI_pair(w3eth, market, WETH_addr, DAI_addr, block_id=web3.eth.Eth.default_block):
    
    pair_addr = market['factory'].functions.getPair(WETH_addr, DAI_addr).call(block_identifier=block_id)
    pair = w3eth.contract(pair_addr, abi=open('script/abi_uniswap_v2_pair.json').read())
    reserve0, reserve1, _ = pair.functions.getReserves().call(block_identifier=block_id)

    token0_addr = pair.functions.token0().call(block_identifier=block_id)
    token1_addr = pair.functions.token1().call(block_identifier=block_id)

    if (token0_addr == WETH_addr) and (token1_addr == DAI_addr):
        DAI_ETH_price = reserve1 / reserve0
    else:
        assert((token1_addr == WETH_addr) and (token0_addr == DAI_addr))
        DAI_ETH_price = reserve0 / reserve1

    return DAI_ETH_price
