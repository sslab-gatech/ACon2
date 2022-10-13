import os, sys
import warnings
import numpy as np
from scipy.stats import multinomial

class RCI:
    def __init__(self, args, model_base):
        super().__init__()
        self.args = args
        self.base = model_base
        self.threshold = self.args.threshold_min
        self.threshold_min = self.args.threshold_min
        self.threshold_max = self.args.threshold_max
        self.eta = self.args.threshold_step
        self.reset()


    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.initialized = False
        self.ps = None
        self.updated = False
        self.err_list = []
        
        
    def error(self, label):
        score = self.base.score(label)
        return (score < self.threshold).astype('float')

    
    def predict(self):
        interval = self.base.superlevelset(self.threshold)
        return interval

    
    def update(self, label):
        
        if label is None:
            return

        if not self.initialized:
            self.base.init_state(label)
            self.initialized = True
        else:
            # check error
            err = self.error(label)
            self.n_err += err
            self.ps = self.predict()
            self.n_obs += 1
            #self.err_list.append(err)

            # update ps
            self.threshold = self.threshold + self.eta*(self.args.alpha - err)
            print(self.eta, self.args.alpha, err, self.threshold)

            self.threshold = max(self.args.threshold_min, self.threshold)
            self.threshold = min(self.args.threshold_max, self.threshold)

            
            self.label = label
            
            # update the base model
            self.base_out = self.base(label)
            
            self.updated = True

            print(self.n_err / self.n_obs)


            
    def summary(self):
        return {
            'obs': self.label,
            'ps': self.ps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
        }
