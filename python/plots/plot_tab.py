import os, sys
import pickle
import numpy as np
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md

import data

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

def print_data(args, exp_name):
    
    # read outputs
    outputs = pickle.load(open(os.path.join(args.output_root, exp_name, 'out.pk'), 'rb'))
    exp_args = outputs['args']
    results = outputs['results']

    # init
    key = exp_args.data.path
    if len(key) == 1:
        name = exp_args.model_ps.name[0]
    else:
        name = 'ACC'
    market_names = [k.split('/')[2].split('_')[0] for k in key]
    print(market_names)
    price_name = '/'.join(key[0].split('/')[1].split('_')[1:])
    print(price_name)
    
    # process results
    K = results[0]['prediction_summary']['K']
    alpha_base = results[0]['prediction_summary']['alpha'][:K]
    alpha = np.sum(alpha_base)
    time = [r['time'] for r in results]
    # if len(key) == 1:
    #     price = [r['observation'][key[0]] for r in results]
    # else:
    #     print(results[0]['observation'])
    price = [[r['observation'][k] for k in key] for r in results]

    itv_min = [max(0, r['prediction_summary']['ps_updated'][0]) for r in results]
    itv_max = [min(max_val, r['prediction_summary']['ps_updated'][1]) for r in results]

    itv_bps = [r['prediction_summary']['base_ps']  for r in results]
    itv_bps = itv_bps[1:]

    # read TWAP results
    ds_TWAP = data.SinglePriceDataset(args.TWAP_data)
    price_TWAP = []
    for t in time:
        price_TWAP.append(1/ds_TWAP.read(t.astype(int)))
    price_TWAP = np.array(price_TWAP)
    
    args.num_data_max = min(args.num_data_max, len(time))
    if args.time_start:
        time_start = np.datetime64(args.time_start)
        for i, t in enumerate(time):
            if time_start <= t:
                data_start_index = i
                break
    else:
        data_start_index = 0
    time = time[data_start_index:args.num_data_max]
    price = price[data_start_index:args.num_data_max]
    price_TWAP = price_TWAP[data_start_index:args.num_data_max]
    
    itv_min = itv_min[data_start_index:args.num_data_max]
    itv_max = itv_max[data_start_index:args.num_data_max]
    itv_bps = itv_bps[data_start_index:args.num_data_max]
        
    
    if args.zoom_end_index == np.inf:
        args.zoom_end_index = len(time)
    time = time[args.zoom_start_index:args.zoom_end_index]
    price = price[args.zoom_start_index:args.zoom_end_index]
    price_TWAP = price_TWAP[args.zoom_start_index:args.zoom_end_index]

    itv_min = itv_min[args.zoom_start_index:args.zoom_end_index]
    itv_max = itv_max[args.zoom_start_index:args.zoom_end_index]
    itv_bps = itv_bps[args.zoom_start_index:args.zoom_end_index]

    # if args.show_base_ps:
    #     data_table = {}
    #     for time_i, price_i, itv_min_i, itv_max_i, itv_bps_i in zip(time, price, itv_min, itv_max, itv_bps):
    #         data_table[time_i] = {key[i]: p for i, p in enumerate(price_i)}
    #         data_table[time_i].update({'acc': [itv_min_i, itv_max_i]})

    #         out_str = f'[{time_i}] ACC = [{itv_min_i:.2f}, {itv_max_i:.2f}]'
    #         for k, v in data_table[time_i].items():
    #             if k is not 'acc':
    #                 key_name = k.split("/")[-1]
    #                 out_str += f', {key_name} = {v if v is not None else 0:.4f}'
    #                 out_str += f', BPS_{key_name} = [{itv_bps_i[k][0]:.2f}, {itv_bps_i[k][1]:.2f}]'
    #         print(out_str)
            
    # median
    price_obs = []
    for i, k in enumerate(key):
        price_i = [p[i] for p in price]
        price_obs.append(price_i)
    price_median = np.median(np.array(price_obs), 0)

    # time
    print('time =', ' & '.join([f'{t}' for t in time]))

    # price data
    for i, k in enumerate(key):
        price_i = [f'{p[i]:.4f}' for p in price]
        print(f'{k} =', ' & '.join(price_i))

    # median
    print('median =', ' & '.join([f'{p:.4f}' for p in price_median]))

    # TWAP
    print('TWAP =', ' & '.join([f'{p:.4f}' for p in price_TWAP]))

    # BPS
    for i, k in enumerate(key):
        itvs = [f'[{itv[k][0]:.2f},{itv[k][1]:.2f}]' for itv in itv_bps]
        print(f'BPS_{k} =', ' & '.join(itvs))

    
    # ACC
    itv_ACC = []
    for mn, mx in zip(itv_min, itv_max):
        if mn == 0 and mx == max_val:
            itv_ACC.append('[$-\infty$,$\infty$]')
        else:
            itv_ACC.append(f'[{mn:.2f},{mx:.2f}]')            
    print('ACC =', ' & '.join(itv_ACC))


    
if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')
    parser.add_argument('--exp_names', type=str, nargs='+', default=
                        [
                            'three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1',
                            'two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1',
                            'one_source_INV_ETH_SushiSwap_K_1_beta_0'
                        ]
    )
    parser.add_argument('--TWAP_data', type=str, default='data/price_ETH_INV/Keep3rV2SushiSwap')
    parser.add_argument('--output_root', type=str, default='output')
    parser.add_argument('--ours_name', type=str, default='ACon$^2$ (ours)')
    parser.add_argument('--fig_root', type=str, default='figs')
    parser.add_argument('--style', type=str, nargs='+', default=['-k', '-r', '-b'])
    parser.add_argument('--fontsize', type=int, default=15)
    parser.add_argument('--time_start', type=str, default='2022-04-02T11:03')
    parser.add_argument('--num_data_max', type=int, default=np.inf)
    parser.add_argument('--y_min', type=float, default=0)
    parser.add_argument('--y_max', type=float, default=10)
    parser.add_argument('--step', type=int, default=1)
    parser.add_argument('--log_scale', action='store_true')
    parser.add_argument('--tag', type=str)
    parser.add_argument('--zoom_start_index', type=int, default=4)
    parser.add_argument('--zoom_end_index', type=int, default=10)
    args = parser.parse_args()
    #color_list = ['C3', 'C4', 'C8', 'C9']
    color_list = ['r', 'b', 'gold', 'C9']
    max_val = 20

    for exp_name in args.exp_names:
        print(exp_name)
        print_data(args, exp_name)
        print()
