import os, sys
import numpy as np
import warnings
import pickle
import glob

import torch as tc
from torch.utils.data import DataLoader

class PriceDataset:
    def __init__(self, path):
        file_names = sorted(glob.glob(path + '*.pk'))
        self.data = [d for f in file_names for d in pickle.load(open(f, 'rb'))]
        
        
    def __getitem__(self, index):
        time, price = self.data[index]['time'], self.data[index]['price']
        #TODO return time
        return index, price


    def __len__(self):
        return len(self.data)

    
class Price:
    def __init__(
            self, data_path,
            batch_size=1,
            num_workers=0,
    ):

        self.seq = DataLoader(PriceDataset(data_path), batch_size=batch_size, shuffle=False, num_workers=num_workers)
        print(f'[price data, data_path = {data_path}] sequence length = {len(self.seq.dataset)}')
     
        
if __name__ == '__main__':
    dsld = Price('price_ETH_USD/coinbase')
