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

if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')
    parser.add_argument('--exp_name', type=str, default='three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1')
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
    parser.add_argument('--zoom_start_index', type=int, default=0)
    parser.add_argument('--zoom_end_index', type=int, default=10)
    parser.add_argument('--show_base_ps', action='store_true')
    args = parser.parse_args()
    #color_list = ['C3', 'C4', 'C8', 'C9']
    color_list = ['r', 'b', 'gold', 'C9']
    max_val = 20
    
    # read outputs
    outputs = pickle.load(open(os.path.join(args.output_root, args.exp_name, 'out.pk'), 'rb'))
    exp_args = outputs['args']
    results = outputs['results']

    # init
    fn_out = os.path.join(args.output_root, 'highlight', args.fig_root, f'plot_ps{"_" if args.tag else ""}{args.tag if args.tag else ""}')

    os.makedirs(os.path.dirname(fn_out), exist_ok=True)
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
    if args.show_base_ps:
        itv_bps = [r['prediction_summary']['base_ps']  for r in results]

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
    if args.show_base_ps:
        itv_bps = itv_bps[data_start_index:args.num_data_max]
        
    
    if args.zoom_end_index == np.inf:
        args.zoom_end_index = len(time)
    time = time[args.zoom_start_index:args.zoom_end_index]
    price = price[args.zoom_start_index:args.zoom_end_index]
    price_TWAP = price_TWAP[args.zoom_start_index:args.zoom_end_index]

    itv_min = itv_min[args.zoom_start_index:args.zoom_end_index]
    itv_max = itv_max[args.zoom_start_index:args.zoom_end_index]
    if args.show_base_ps:
        itv_bps = itv_bps[args.zoom_start_index:args.zoom_end_index]

    if args.show_base_ps:
        data_table = {}
        for time_i, price_i, itv_min_i, itv_max_i, itv_bps_i in zip(time, price, itv_min, itv_max, itv_bps):
            data_table[time_i] = {key[i]: p for i, p in enumerate(price_i)}
            data_table[time_i].update({'acc': [itv_min_i, itv_max_i]})

            out_str = f'[{time_i}] ACC = [{itv_min_i:.2f}, {itv_max_i:.2f}]'
            for k, v in data_table[time_i].items():
                if k is not 'acc':
                    key_name = k.split("/")[-1]
                    out_str += f', {key_name} = {v if v is not None else 0:.4f}'
                    out_str += f', BPS_{key_name} = [{itv_bps_i[k][0]:.2f}, {itv_bps_i[k][1]:.2f}]'
            print(out_str)


    # plot prediction set results
    with PdfPages(fn_out + '.pdf') as pdf:
        hs = []
        plt.figure(1)
        plt.clf()
        fig, ax = plt.subplots()

        # prediction set
        h = plt.fill_between(time[::args.step], itv_max[::args.step], itv_min[::args.step], color='green', alpha=0.4, label=args.ours_name)
        hs.append(h)
        print(itv_max)
        
        # observations
        price_obs = []
        for i, k in enumerate(key):
            price_i = [p[i] for p in price]
            price_obs.append(price_i)
            t_i = [t for j, t in enumerate(time) if price_i[j] is not None]
            p_i = [p for j, p in enumerate(price_i) if price_i[j] is not None]
            h = plt.plot(t_i[::args.step], p_i[::args.step], marker='s', label=market_names[i], linewidth=1.0, color=color_list[i])
            hs.append(h[0])

        # median
        price_median = np.median(np.array(price_obs), 0)
        h = plt.plot(t_i[::args.step], price_median[::args.step], 'k-', label='median', linewidth=2.0)
        hs.append(h[0])

        #TWAP
        h = plt.plot(t_i[::args.step], price_TWAP[::args.step], 'k--', label='TWAP (Keep3rV2)', linewidth=2.0)
        hs.append(h[0])
        
        # beautify
        plt.gca().xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.xticks( rotation=20 )
        ymin = np.min(price) * 0.5 if args.y_min is None else args.y_min
        ymax = np.max(price) * 2 if args.y_max is None else args.y_max
        plt.ylim((ymin, ymax))
        if args.log_scale:
            plt.yscale('log')
        plt.xlabel('time', fontsize=args.fontsize)
        plt.ylabel(f'price ({price_name})', fontsize=args.fontsize)
        plt.grid('on')
        plt.legend(handles=hs, fontsize=args.fontsize)

        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        print(fn_out)

