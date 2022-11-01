import os, sys
import pickle
import numpy as np
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset

if __name__ == '__main__':

    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')
    parser.add_argument('--exp_name', type=str, default='single_source_INV_ETH_SushiSwap')
    parser.add_argument('--output_root', type=str, default='output')
    parser.add_argument('--ours_name', type=str, default='ACon$^2$')
    parser.add_argument('--fig_root', type=str, default='figs')
    parser.add_argument('--style', type=str, nargs='+', default=['-k', '-r', '-b'])
    parser.add_argument('--fontsize', type=int, default=15)
    parser.add_argument('--time_start', type=str)
    parser.add_argument('--num_data_max', type=int, default=np.inf)
    parser.add_argument('--y_min', type=float)
    parser.add_argument('--y_max', type=float)
    parser.add_argument('--step', type=int, default=1)
    parser.add_argument('--y_max_mc', type=float)
    parser.add_argument('--log_scale', action='store_true')
    parser.add_argument('--tag', type=str)
    parser.add_argument('--zoom_start_index', type=int, default=0)
    parser.add_argument('--zoom_end_index', type=int, default=np.inf)
    parser.add_argument('--show_base_ps', action='store_true')
    args = parser.parse_args()
    color_list = ['C3', 'C4', 'C8', 'C9']
    max_val = 1e4
    
    # read outputs
    outputs = pickle.load(open(os.path.join(args.output_root, args.exp_name, 'out.pk'), 'rb'))
    exp_args = outputs['args']
    results = outputs['results']

    # init
    fn_out = os.path.join(args.output_root, args.exp_name, args.fig_root, f'plot_ps{"_" if args.tag else ""}{args.tag if args.tag else ""}')
    fn_out_miscoverage = os.path.join(args.output_root, args.exp_name, args.fig_root, f'plot_miscoverage{"_" if args.tag else ""}{args.tag if args.tag else ""}')

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
    n_err = [r['prediction_summary']['n_err'] for r in results]
    n_obs = [r['prediction_summary']['n_obs'] for r in results]
    n_err_base = [r['prediction_summary']['n_err_base'] for r in results]
    n_obs_base = [r['prediction_summary']['n_obs_base'] for r in results]

    itv_min = [max(0, r['prediction_summary']['ps_updated'][0]) for r in results]
    itv_max = [min(max_val, r['prediction_summary']['ps_updated'][1]) for r in results]
    if args.show_base_ps:
        itv_bps = [r['prediction_summary']['base_ps']  for r in results]
        
    
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
    itv_min = itv_min[data_start_index:args.num_data_max]
    itv_max = itv_max[data_start_index:args.num_data_max]
    if args.show_base_ps:
        itv_bps = itv_bps[data_start_index:args.num_data_max]
    n_err = n_err[data_start_index:args.num_data_max]
    n_obs = n_obs[data_start_index:args.num_data_max]
    n_err_base = n_err_base[data_start_index:args.num_data_max]
    n_obs_base = n_obs_base[data_start_index:args.num_data_max]
        
    
    if args.zoom_end_index == np.inf:
        args.zoom_end_index = len(time)
    time = time[args.zoom_start_index:args.zoom_end_index]
    price = price[args.zoom_start_index:args.zoom_end_index]
    itv_min = itv_min[args.zoom_start_index:args.zoom_end_index]
    itv_max = itv_max[args.zoom_start_index:args.zoom_end_index]
    if args.show_base_ps:
        itv_bps = itv_bps[args.zoom_start_index:args.zoom_end_index]
    n_err = n_err[args.zoom_start_index:args.zoom_end_index]
    n_obs = n_obs[args.zoom_start_index:args.zoom_end_index]
    n_err_base = n_err_base[args.zoom_start_index:args.zoom_end_index]
    n_obs_base = n_obs_base[args.zoom_start_index:args.zoom_end_index]

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

        # ----- an inset
        inset_zoom_start_index = int(1.8*len(time)//3) - 100
        inset_zoom_end_index = int(1.8*len(time)//3) + 100
        time_inset = time[inset_zoom_start_index:inset_zoom_end_index]
        itv_max_inset = itv_max[inset_zoom_start_index:inset_zoom_end_index]
        itv_min_inset = itv_min[inset_zoom_start_index:inset_zoom_end_index]
        ax_inset = ax.inset_axes([0.03, 0.5, 0.47, 0.47])
        
        # prediction set
        ax_inset.fill_between(time_inset, itv_max_inset, itv_min_inset, color='green', alpha=0.4, label=args.ours_name)
        
        # observations
        for i, k in enumerate(key):
            price_i = [p[i] for p in price]
            t_i = [t for j, t in enumerate(time) if price_i[j] is not None]
            p_i = [p for j, p in enumerate(price_i) if price_i[j] is not None]
            h = ax_inset.plot(
                t_i[inset_zoom_start_index:inset_zoom_end_index],
                p_i[inset_zoom_start_index:inset_zoom_end_index],
                label=market_names[i], linewidth=1.0, color=color_list[i])
        

        # ----- the original plot
        
        # prediction set
        h = plt.fill_between(time[::args.step], itv_max[::args.step], itv_min[::args.step], color='green', alpha=0.4, label=args.ours_name)
        hs.append(h)

        
        # observations
        for i, k in enumerate(key):
            price_i = [p[i] for p in price]
            t_i = [t for j, t in enumerate(time) if price_i[j] is not None]
            p_i = [p for j, p in enumerate(price_i) if price_i[j] is not None]
            h = plt.plot(t_i[::args.step], p_i[::args.step], label=market_names[i], linewidth=1.0, color=color_list[i])
            hs.append(h[0])

        # beautify
        plt.gca().xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d %H:%M'))
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

        # beautify an inset
        ax_inset.set_xticks([], [])
        ax_inset.set_yticks([], []) 
        ax.indicate_inset_zoom(ax_inset, edgecolor="black")
        
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        print(fn_out)

    # plot the miscoverage rate
    with PdfPages(fn_out_miscoverage + '.pdf') as pdf:
        hs = []
        plt.figure(1)
        plt.clf()

        miscoverage = [e/n for e, n in zip(n_err, n_obs)]
        y_max = min(np.max(miscoverage)*1.5, 1.5*alpha)

        # a desired miscoverage
        h = plt.hlines(alpha, 0, len(miscoverage), colors='k', linestyles='solid', label=r'$\alpha = %.3f$'%(alpha))
        hs.append(h)
        
        # a desired miscoverage
        assert(all(alpha_base[0] == np.array(alpha_base)))
        h = plt.hlines(alpha_base[0], 0, len(miscoverage), colors='k', linestyles='dashed', label=r'$\alpha_{base} = %.3f$'%(alpha_base[0]))
        hs.append(h)

        # miscoverage
        h = plt.plot(miscoverage, '-', color='C2', label=args.ours_name)
        hs.append(h[0])

        # miscoverage rate of bases
        for i, k in enumerate(n_err_base[0].keys()):
            src_name = k.split('/')[-1]
            # miscoverage
            m = [e[k]/n[k] for e, n in zip(n_err_base, n_obs_base)]
            h = plt.plot(m[::args.step], '-', color=color_list[i], label=r'$BPS_{%s}$'%(src_name))
            hs.append(h[0])
            
        
        # beautify
        plt.xlabel('# observations', fontsize=args.fontsize)
        plt.ylabel(f'miscoverage rate', fontsize=args.fontsize)
        plt.grid('on')
        plt.xticks(fontsize=args.fontsize*0.75)
        plt.yticks(fontsize=args.fontsize*0.75)
        plt.ylim([0, args.y_max_mc if args.y_max_mc else alpha*1.5])
        plt.legend(handles=hs, fontsize=args.fontsize)
        plt.savefig(fn_out_miscoverage+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        print(fn_out_miscoverage)
