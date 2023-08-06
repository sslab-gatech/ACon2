import os, sys
import pickle

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as md

if __name__ == '__main__':

    fontsize = 15
    data_info = [
        #{'name': 'coinbase', 'path': 'data/price_ETH_USD/coinbase.pk', 'style': 'b-'},
        {'name': 'UniswapV2', 'path': 'data/price_ETH_USD/UniswapV2.pk', 'style': 'r-'},
    ]
    fn_out = 'output/figs/data/summary'

    os.makedirs(os.path.dirname(fn_out), exist_ok=True)

    with PdfPages(fn_out + '.pdf') as pdf:
        plt.figure(1)
        hs = []
        for di in data_info:
            data = pickle.load(open(di['path'], 'rb'))
            time = [d['time'].astype('datetime64[s]') for d in data]
            price = [d['price'] for d in data]

            h = plt.plot(time, price, di['style'], label=di['name'])
            hs.append(h[0])

        plt.gca().xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d'))
        plt.xticks( rotation=20 )
        plt.xlabel('time', fontsize=fontsize)
        plt.ylabel('price (USD)', fontsize=fontsize)
        plt.grid('on')
        plt.legend(handles=hs, fontsize=fontsize)
        plt.savefig(fn_out+'.png', bbox_inches='tight')
        pdf.savefig(bbox_inches='tight')
        
