import os, sys
import pickle
import numpy as np
import argparse
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md


if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='data plot')
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, default='read_acc')
    parser.add_argument('--fig_root', type=str, default='output/figs')
    parser.add_argument('--style', type=str, nargs='+', default=['-k', '-r', '-b'])
    parser.add_argument('--fontsize', type=int, default=15)
    parser.add_argument('--data_start_idx', type=int, default=0)
    parser.add_argument('--data_end_idx', type=int, default=4000)
    parser.add_argument('--y_min', type=float, default=0.0)
    parser.add_argument('--y_max', type=float, default=3.0)
    parser.add_argument('--max_val', type=float, default=100)
    parser.add_argument('--log_scale', action='store_true')
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--ours_name', type=str, default='ACon$^2$')


    args = parser.parse_args()
    
    # init
    fn_out = os.path.join(args.fig_root, args.exp_name, f'plot_ps{"_" if args.tag else ""}{args.tag}')
    os.makedirs(os.path.dirname(fn_out), exist_ok=True)

    # read data
    data_path = os.path.join(args.output_dir, args.exp_name, 'data.pk')
    data = pickle.load(open(data_path, 'rb'))
    t = np.arange(len(data))
    data = data[args.data_start_idx:args.data_end_idx]
    t = t[args.data_start_idx:args.data_end_idx]

    #market_names = data[0].market_names
    market_names = ['Pool1', 'Pool2', 'Pool3']
    price_data = {k: [d['prices'][i] for d in data] for i, k in enumerate(market_names)}
    itv_min = [max(d['interval'][0], -args.max_val) for d in data]
    itv_max = [min(d['interval'][1], args.max_val) for d in data]
    
    with PdfPages(fn_out + '.pdf') as pdf:
        hs = []
        plt.figure(1)

        
        # observations
        for i, (k, v) in enumerate(price_data.items()):
            v = np.minimum(np.maximum(0, v), args.max_val)
            h = plt.plot(t, v, args.style[i], label=market_names[i], linewidth=0.4)
            hs.append(h[0])

        # prediction set
        h = plt.fill_between(t, itv_max, itv_min, color='green', alpha=0.7, label=args.ours_name)
        hs.append(h)

        # beautify
        ymin = args.y_min
        ymax = args.y_max
        plt.ylim((ymin, ymax))
        if args.log_scale:
            plt.yscale('log')
        plt.xlabel('time', fontsize=args.fontsize)
        plt.ylabel(f'price', fontsize=args.fontsize)
        plt.grid('on')
        plt.legend(handles=hs, fontsize=args.fontsize)
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        time.sleep(1)

        print(fn_out)
