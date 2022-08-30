import os, sys
import numpy as np
import warnings
import pickle
import glob

import torch as tc
from torch.utils.data import DataLoader

class NoObservation(Exception):
    pass

class SinglePriceDataset:
    def __init__(self, path):
        file_names = sorted(glob.glob(path + '*.pk'))
        self.data = [d for f in file_names for d in pickle.load(open(f, 'rb'))]
        
        # time type conversion
        for i in range(len(self.data)):
            self.data[i]['time'] = self.data[i]['time'].astype('datetime64[s]')
            self.data[i]['price'] = float(self.data[i]['price']) if type(self.data[i]['price']) is not float else self.data[i]['price']
        
        # check if data is sorted
        timestamps = [d['time'].astype('int') for d in self.data]
        for t1, t2 in zip(timestamps[:-1], timestamps[1:]):
            assert(t1 <= t2)

        self.reset()
        
        
    def __getitem__(self, index):
        time, price = self.data[index]['time'], self.data[index]['price']
        return {'timestamp': time.astype('int'), 'price': price}


    def __len__(self):
        return len(self.data)


    def reset(self):
        self.index = 0


    def read(self, timestamp):

        if self.index == len(self):
            raise StopIteration
        
        index = None
        for i, d in enumerate(self.data[self.index:]):
            if d['time'].astype('int') > timestamp:
                break
            else:
                index = i + self.index

        if index is None:
            raise NoObservation
        else:
            self.index = index + 1
            return self[index]


class PriceDataset:
    def __init__(
            self, data_path,
    ):
        self.seq = {}
        for p in data_path:
            seq = SinglePriceDataset(p)
            print(f'[price data, data_path = {p}] sequence length = {len(seq)}')
            self.seq[p] = seq

    def reset(self):
        for k in self.seq.keys():
            self.seq[k].reset()
            
    def read(self, time):
        out = {}
        for k in self.seq.keys():
            try:
                out[k] = self.seq[k].read(time.astype('int'))
            except NoObservation:
                out[k] = None
        return out            
        
if __name__ == '__main__':
    dsld = Price('price_ETH_USD/coinbase')
