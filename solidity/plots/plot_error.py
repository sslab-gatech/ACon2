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
    parser.add_argument('--y_max', type=float, default=0.012)
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--n_sources', type=int, default=3)
    #parser.add_argument('--alpha_list', type=str, nargs='+', default=['0d03', '0d15', '0d3'])
    parser.add_argument('--K', type=int, default=3)
    parser.add_argument('--alpha', type=str, default='0.01')
    parser.add_argument('--duration', type=int, default=3600)
    parser.add_argument('--exp_index', type=int, default=1)

    args = parser.parse_args()
    
    # init
    #fn_out = os.path.join(args.fig_root, args.exp_name, f'plot_error_var_K_{args.K}_alpha{"_" if args.tag else ""}{args.tag}')
    fn_out = os.path.join(args.fig_root, args.exp_name, f'plot-error-var-K-{args.K}-alpha-{args.alpha.replace(".", "d")}')
    os.makedirs(os.path.dirname(fn_out), exist_ok=True)

    # read data
    error = []
    t_list = []
    
    data_path_list = glob.glob(os.path.join(args.output_dir, f'{args.exp_name}_K_{args.K}_alpha_{args.alpha.replace(".", "d")}_iter_{args.exp_index}_duration_{args.duration}', 'data.pk'))
    print(data_path_list)
    for p in data_path_list:
        data = pickle.load(open(p, 'rb'))
        error = [d['miscoverage_cons'] for d in data]
        print(p, len(error))
    t = np.arange(len(error))
    t_list.append(t)

    with PdfPages(fn_out + '.pdf') as pdf:
        hs = []
        plt.figure(1)

        # error
        h = plt.plot(t, error, linewidth=2, color='g')

        # alpha
        h = plt.hlines(float(args.alpha), min(t), max(t), colors='k', linestyles='solid', label=rf'$\alpha={args.alpha}$')
        hs.append(h)
        
        # beautify
        plt.ylim((args.y_min, args.y_max))
        plt.xlabel('# observations', fontsize=args.fontsize)
        plt.ylabel(f'pseudo-miscoverage rate', fontsize=args.fontsize)
        plt.grid('on')
        #plt.yticks(list(set(list(plt.yticks()[0]) + [float(e)  for e in args.alpha_list])))
        plt.legend(handles=hs, fontsize=args.fontsize)
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')

        print(fn_out)
