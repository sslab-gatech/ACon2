import os, sys
import pickle
import numpy as np
import argparse
import time

if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='data plot')
    parser.add_argument('--alg_output_dir', type=str, default='output')
    parser.add_argument('--baseline_dir', type=str, default='baseline')
    parser.add_argument('--acon2_dir', type=str, default='acon2_K_3_alpha_0d001_iter_1_duration_3600')

    args = parser.parse_args()


    print('==========  Gas usage averaged over 500 transactions ==========')
    # baseline gas
    gas_hist = pickle.load(open(os.path.join(args.alg_output_dir, args.baseline_dir, 'trader1', 'gas_data.pk'), 'rb'))
    print(f'Swap (G_Swap) = {np.mean(gas_hist)} +- {np.std(gas_hist)}')

    # Swap+BPS
    gas_hist = pickle.load(open(os.path.join(args.alg_output_dir, args.acon2_dir, 'trader1', 'gas_data.pk'), 'rb'))
    print(f'Swap+BPS (G_Swap+G_BPS) = {np.mean(gas_hist)} +- {np.std(gas_hist)}')
    

    # ACon2
    gas_hist = pickle.load(open(os.path.join(args.alg_output_dir, args.acon2_dir, 'gas_data.pk'), 'rb'))
    print(f'ACon2 (G_ACon2) = {np.mean(gas_hist)} +- {np.std(gas_hist)}')
