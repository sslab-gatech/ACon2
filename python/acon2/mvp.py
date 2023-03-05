import os, sys
import warnings
import numpy as np
from scipy.stats import multinomial

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import logsumexp

# MVP algorithm for a single group
class SpecialMVP:
    def __init__(self, args, model_base):
        super().__init__()
        self.args = args
        self.base = model_base
        self.eta = self.args.eta
        self.n_bins = self.args.n_bins
        self.r = 1000 # not sensitive on results
        self.e = 1.0 # not sensitive on results
        self.label_noise_factor = 0.0
        self.reset()


    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.initialized = False
        self.ps = None

        self.thres_cnt = np.zeros(self.n_bins)
        self.corr_cnt = np.zeros(self.n_bins)
        #self.norm_func = lambda n: np.sqrt((n+1) * np.power(np.log2(n+2), 1 + self.e))
        assert(self.e == 1)
        self.norm_func = lambda n: np.sqrt((n+1) * (np.log2(n+2)**2))
        
        
    def error(self, label):
        score = self.base.score(label)

        itv = self.predict()
        if itv[0] <= label and label <= itv[1]:
            return 0.0
        else:
            return 1.0

    
    def predict(self):
        interval = self.base.superlevelset(self.threshold)
        return interval

    
    def init_or_update(self, label):
        
        if label is None:
            return

        def find_threshold_mvp():
            
            w_prev = np.exp( self.eta * self.corr_cnt[0] / self.norm_func(self.thres_cnt[0]) ) - \
                     np.exp(-self.eta * self.corr_cnt[0] / self.norm_func(self.thres_cnt[0]) )

            if w_prev > 0:
                pos = True
            else:
                pos = False

            for i in range(1, self.n_bins):
                
                w_cur = np.exp( self.eta * self.corr_cnt[i] / self.norm_func(self.thres_cnt[i]) ) - \
                        np.exp(-self.eta * self.corr_cnt[i] / self.norm_func(self.thres_cnt[i]) )

                if w_cur > 0:
                    pos = True
                else:
                    pos = False

                if w_cur * w_prev <= 0:

                    Z = np.abs(w_cur) + np.abs(w_prev)
                    if Z == 0:
                        b = 1
                    else:
                        b = np.abs(w_cur) / Z

                    if np.random.rand() <= b:
                        thres = (i) / self.n_bins - 1.0 /(self.r * self.n_bins)
                     
                        # return thres
                        return 1 - thres
                    else:
                        thres = (i) / self.n_bins
                        # return thres
                        return 1 - thres
                    
                w_prev = w_cur
                
            if pos:
                return 1.0
            else:
                return 0.0


        # add noise to
        if not self.initialized:
            self.base.init_state(label)
            self.initialized = True
            self.threshold = find_threshold_mvp()
            print("init th =", self.threshold)
        else:
            
            # check error before ps update
            err = self.error(label)
            self.n_err += err
            self.n_obs += 1
            self.label = label
            self.ps = self.predict()            
            
            print(f'[MVP] threshold = {self.threshold:.4f}, score = {self.base.score(label):.4f}, size = {self.ps[1] - self.ps[0]:.4f}, '
                  f'interval = [{self.ps[0]:.4f}, {self.ps[1]:.4f}], obs = {label:.4f}, '
                  f'error_cur = {err}, '
                  f'error = {self.n_err / self.n_obs:.4f}'
            )
            
            # update stats
            bin_idx = min(int((1 - self.threshold) * self.n_bins + 0.5/self.r), self.n_bins - 1)            
            self.thres_cnt[bin_idx] += 1
            self.corr_cnt[bin_idx] += self.args.alpha - err

            # recompute a threshold
            self.threshold = find_threshold_mvp()

            # update the base model
            self.base.update(label)

            
            
    def summary(self):
        return {
            'obs': self.label,
            'ps': self.ps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
        }
