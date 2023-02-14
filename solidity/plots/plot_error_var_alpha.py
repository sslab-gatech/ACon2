import os, sys
import pickle
import numpy as np
import argparse
import time
import glob

import matplotlib
import matplotlib.ticker as ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md


if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='data plot')
    parser.add_argument('--output_dir', type=str, default='output')
    parser.add_argument('--exp_name', type=str, default='acon2')
    parser.add_argument('--fig_root', type=str, default='output/figs')
    # parser.add_argument('--style', type=str, nargs='+', default=['-k', '-r', '-b'])
    parser.add_argument('--fontsize', type=int, default=15)
    # parser.add_argument('--data_start_idx', type=int, default=0)
    # parser.add_argument('--data_end_idx', type=int, default=2000)
    parser.add_argument('--y_min', type=float, default=0.0)
    parser.add_argument('--y_max', type=float, default=0.05)
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--n_sources', type=int, default=3)
    #parser.add_argument('--alpha_list', type=str, nargs='+', default=['0d03', '0d15', '0d3'])
    parser.add_argument('--alpha_list', type=str, nargs='+', default=['0.01', '0.001'])
    parser.add_argument('--alpha_color', type=str, nargs='+', default=['green', 'red', 'blue'])
    parser.add_argument('--duration', type=int, default=1800)

    args = parser.parse_args()
    
    # init
    fn_out = os.path.join(args.fig_root, args.exp_name, f'plot_error_var_alpha{"_" if args.tag else ""}{args.tag}')
    os.makedirs(os.path.dirname(fn_out), exist_ok=True)

    # read data
    error_min_list = []
    error_max_list = []
    error_mean_list = []
    alpha_list = []
    alpha_color_list = []
    t_list = []
    for alpha_color, alpha_str in zip(args.alpha_color, args.alpha_list):
        data_path_list = glob.glob(os.path.join(args.output_dir, f'{args.exp_name}_basealpha_{alpha_str.replace(".", "d")}_iter_*_duration_{args.duration}', 'data.pk'))
        print(data_path_list)
        error_stack = []
        for p in data_path_list:
            data = pickle.load(open(p, 'rb'))
            error = [d['miscoverage_cons'] for d in data]
            error_stack.append(error)
            print(p, len(error))
        if len(error_stack) == 0:
            continue
        len_min = min([len(error) for error in error_stack])
        error_stack = [error[:len_min] for error in error_stack]
        error_stack = np.array(error_stack)
        error_min = np.amin(error_stack, 0)
        error_max = np.amax(error_stack, 0)
        error_mean = np.mean(error_stack, 0)
        t = np.arange(len(error_min))
        t_list.append(t)
        error_min_list.append(error_min)
        error_max_list.append(error_max)
        error_mean_list.append(error_mean)
        alpha_list.append(alpha_str)
        alpha_color_list.append(alpha_color)

    with PdfPages(fn_out + '.pdf') as pdf:
        hs = []
        plt.figure(1)

        # pseudo-miscoverage rate range
        for error_min, error_max, error_mean, t, alpha_str, color in zip(error_min_list, error_max_list, error_mean_list, t_list, alpha_list, alpha_color_list):
            alpha_acon2 = float(alpha_str) * args.n_sources

            # mean
            h = plt.plot(t, error_mean, color=color, linewidth=2)
                
            # min/max
            h = plt.fill_between(t, error_max, error_min, color=color, alpha=0.2, label=rf'ACC with $\alpha={alpha_acon2}$')
            hs.append(h)

            # alpha
            h = plt.hlines(alpha_acon2, min(t), max(t), colors='k', linestyles='solid', label=rf'$\alpha={alpha_acon2}$')

            
        # beautify
        plt.ylim((args.y_min, args.y_max))
        plt.xlabel('# observations', fontsize=args.fontsize)
        plt.ylabel(f'miscoverage rate', fontsize=args.fontsize)
        plt.grid('on')
        plt.yticks(list(plt.yticks()[0]) + [float(e) * args.n_sources for e in args.alpha_list])
        plt.legend(handles=hs, fontsize=args.fontsize)
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')

        print(fn_out)
