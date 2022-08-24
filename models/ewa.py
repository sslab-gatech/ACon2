import os, sys
import warnings
#import torch as tc
import numpy as np
from scipy.stats import multinomial

class EWA1D:
    def __init__(self, args, model_base):
        super().__init__()
        self.args = args
        self.base = model_base
        self.threshold = self.args.threshold_min
        self.thresholds = np.arange(self.args.threshold_min, self.args.threshold_max+self.args.threshold_step, self.args.threshold_step)
        self.eta = np.sqrt(2.0 * np.log(len(self.thresholds)) / self.args.T)
        self.q = np.ones(len(self.thresholds)) / len(self.thresholds)
        self.small_val = 1e-8

        
    def error(self, label):
        score = self.base.score(label)
        return (score < self.threshold).astype('float')
    

    def update(self, label):
        
        score = self.base.score(label)
        err = (score < self.thresholds).astype('float')
        
        # corr_ind = err == False
        # n_corrs = np.sum(corr_ind)
        # err = err.astype('float')

        # err_ori = np.copy(err)
        # err[corr_ind] = 0.1*((n_corrs - np.arange(1, n_corrs+1)) / n_corrs)

        # self.q = self.q * np.exp(-self.eta*(err - self.args.alpha))
        
        self.q = self.q * np.exp(-self.eta*(err - self.args.alpha))
        self.q = self.q / (np.sum(self.q) + self.small_val)

        print(np.argmax(self.q))

        

    def predict(self):
        self.threshold = self.thresholds[np.argmax(multinomial.rvs(1, self.q))]
        interval = self.base.superlevelset(self.threshold)
        return interval
    

                
        

        
