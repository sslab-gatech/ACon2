import os, sys
import pickle
import numpy as np
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')
    parser.add_argument('--exp_names', type=str, nargs="+",
                        default=[
                            'one_source_INV_ETH_SushiSwap_K_1_beta_0',
                            'two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1',
                            'three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1',
                        ])
    parser.add_argument('--output_root', type=str, default='output')
    parser.add_argument('--alg_output_root', type=str, default='output')

    parser.add_argument('--fig_root', type=str, default='figs')
    # parser.add_argument('--style', type=str, nargs='+', default=['-k', '-r', '-b'])
    parser.add_argument('--fontsize', type=int, default=15)
    # parser.add_argument('--time_start', type=str)
    # parser.add_argument('--num_data_max', type=int, default=np.inf)
    # parser.add_argument('--y_min', type=float)
    # parser.add_argument('--y_max', type=float)
    # parser.add_argument('--y_max_mc', type=float)
    # parser.add_argument('--log_scale', action='store_true')
    # parser.add_argument('--tag', type=str)
    # parser.add_argument('--zoom_start_index', type=int, default=0)
    # parser.add_argument('--zoom_end_index', type=int, default=np.inf)
    # parser.add_argument('--show_base_ps', action='store_true')
    parser.add_argument('--log_scale', action='store_true')

    args = parser.parse_args()
    # color_list = ['C3', 'C4', 'C8', 'C9']
    fontsize = args.fontsize
    fn_out = os.path.join(args.output_root, "_".join(args.exp_names), args.fig_root, 'plot_size')
    os.makedirs(os.path.dirname(fn_out), exist_ok=True)
    
    # read outputs
    size_dict = {}
    for exp_name in args.exp_names:
        outputs = pickle.load(open(os.path.join(args.alg_output_root, exp_name, 'out.pk'), 'rb'))
        K = int(exp_name[exp_name.find('K_')+2])
        size_dict[K] = [r['prediction_summary']['ps_updated'][1] - r['prediction_summary']['ps_updated'][0] for r in outputs['results']]

        
    # plot prediction set size
    with PdfPages(fn_out + '.pdf') as pdf:
        hs = []
        plt.figure(1, figsize=[5.0, 5.0])
        plt.clf()
        
        name_list = [f'K={k}' for k in size_dict.keys()]
        size_dist = [np.array(size_dict[k]) for k in size_dict.keys()]
        idk_cnt = []
        for i in range(len(size_dist)):
            idk_idx = np.abs(size_dist[i]) == np.inf
            idk_cnt.append(np.mean(idk_idx))
            size_dist[i] = size_dist[i][~idk_idx]
            print(f'mean(size) = {np.mean(size_dist[i])}')
            
        #print(np.max(size_dist[1]))
        print('IDK count =', idk_cnt)
        width = 0.2

        # box plots for size distributions
        # fig, ax1 = plt.subplots()
        # ax2 = ax1.twinx()

        hs = []
        h = plt.boxplot(
            size_dist, whis=np.inf, showmeans=True,
            boxprops=dict(linewidth=3), medianprops=dict(linewidth=3.0),
            # positions=np.arange(1, len(size_dist)+1)-width/2
            #label='interval length'
        )
        hs.append(h["boxes"][0])

        # h = ax2.bar(np.arange(1, len(idk_cnt)+1)+width/2, idk_cnt, width=width)
        # hs.append(h)
        
        plt.gca().set_xticklabels(name_list, fontsize=fontsize)
        plt.ylabel('interval length', fontsize=fontsize)
        plt.gca().tick_params('y', labelsize=fontsize*0.75)
        plt.grid('on')
        if args.log_scale:
            plt.yscale('log')
        else:
            plt.ylim(bottom=0.0)

        # plt.legend(handles=hs, fontsize=fontsize, labels=['size', 'IDK'])
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        print(f'[size distribution] {fn_out}')

    sys.exit()
