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
        file_name = glob.glob(path + '*.pk')
        if len(file_name) == 0:
            path_split = path.split('/')
            pair_name = path_split[-2]
            pair_name_split = pair_name.split('_')
            pair_name = '_'.join([pair_name_split[0], pair_name_split[2], pair_name_split[1]])
            path_split[-2] = pair_name
            path = '/'.join(path_split)
            
            file_name = glob.glob(path + '*.pk')
            assert(len(file_name) == 1)
            self.inverse_price = True
        else:
            assert(len(file_name) == 1)
            self.inverse_price = False
            
        file_name = file_name[0]
        self.data = pickle.load(open(file_name, 'rb'))
        

        # check if data is sorted
        timestamps = [d['time'] for d in self.data]
        for t1, t2 in zip(timestamps[:-1], timestamps[1:]):
            assert t1 <= t2, f'data is not sorted: {t1} > {t2}'

        # time type conversion
        for i in range(len(self.data)):
            self.data[i]['time'] = self.data[i]['time'].astype('datetime64[s]')
            self.data[i]['price'] = float(self.data[i]['price']) if type(self.data[i]['price']) is not float else self.data[i]['price']
        

        self.reset()
        
        
    def __getitem__(self, index):
        time, price = self.data[index]['time'], self.data[index]['price']
        if self.inverse_price:
            price = 1 / price
        return {'timestamp': time.astype('int'), 'price': price}


    def __len__(self):
        return len(self.data)


    def reset(self):
        self.index = 0


    def read(self, timestamp):

        if self.index + 1 == len(self):
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
            self.index = index
            return self[index]['price']


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


class RandomPriceDataset:
    def __init__(self, path, sig=5, seed=None):
        assert(len(path) == 1)
        self.path = path[0] #TODO: dummy
        self.sig = sig
        self.price = 0.0
        np.random.seed(seed)

    def _read(self):
        self.price = np.random.normal(loc=self.price, scale=self.sig)
        #self.price += 2.0
        return self.price
        
    def reset(self):
        self.price = 0.0

    def read(self, time):
        return {self.path: self._read()}

    
class ZeroPriceDataset:
    def __init__(self, path, sig=5, seed=None):
        self.path = path[0] #TODO: dummy
        self.reset()

        
    def _read(self):
        return self.price
        
    def reset(self):
        self.price = 0.0

        
    def read(self, time):
        return {self.path: self._read()}
        
    
if __name__ == '__main__':
    dsld = Price('price_ETH_USD/coinbase')
