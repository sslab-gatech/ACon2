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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add init code hash')
    parser.add_argument('--src_file', type=str, default='src/AMM/UniswapV2/periphery/contracts/libraries/UniswapV2Library.sol.template')
    parser.add_argument('--tar_file', type=str, default='src/AMM/UniswapV2/periphery/contracts/libraries/UniswapV2Library.sol')
    parser.add_argument('--hash', type=str, required=True)
    args = parser.parse_args()

    hash_code = args.hash
    if hash_code[:2] == '0x':
        hash_code = hash_code[2:]
    code = open(args.src_file).read()
    code = code.replace('96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f', f"{hash_code}")
    open(args.tar_file, 'w').write(code)
    
