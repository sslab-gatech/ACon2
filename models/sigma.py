import os, sys
import warnings
import numpy as np
from scipy.stats import multinomial

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import logsumexp


class OneSigma:
    def __init__(self, args, model_base):
        super().__init__()
        self.args = args
        self.base = model_base
        self.reset()


    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.initialized = False
        self.ps = None

                
    def error(self, label):
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

        if not self.initialized:
            self.base.init_state(label)
            self.initialized = True
            self.threshold = find_threshold_mvp()
        else:
            
            # check error before update
            err = self.error(label)
            self.n_err += err
            self.n_obs += 1
            # print(f'MVP: error = {self.n_err}, n = {self.n_obs}')
            
            # predict
            self.ps = self.predict()            
            
            # update stats
            # bin_idx = min(int((self.threshold) * self.n_bins + 0.5/self.r), self.n_bins - 1)
            bin_idx = min(int((1 - self.threshold) * self.n_bins + 0.5/self.r), self.n_bins - 1)
            
            self.thres_cnt[bin_idx] += 1
            self.corr_cnt[bin_idx] += self.args.alpha - err #TODO

            # print(self.corr_cnt)
            
            # update a threshold
            ##DGB
            # self.threshold = 1 - find_threshold_mvp()
            self.threshold = find_threshold_mvp()
            
            print(f'[MVP] threshold = {self.threshold:.4f}, size = {self.ps[1] - self.ps[0]:.4f}, '
                  f'interval = [{self.ps[0]:.4f}, {self.ps[1]:.4f}], obs = {label:.4f}, '
                  f'error_cur = {err}, '
                  f'error = {self.n_err / self.n_obs:.4f}'
            )


            # update the base model
            self.base_out = self.base(label)

            self.label = label
            # self.updated = True
            
            # print(f'miscoverage = {self.n_err / self.n_obs:.4f}')
            
    def summary(self):
        return {
            'obs': self.label,
            'ps': self.ps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
        }
