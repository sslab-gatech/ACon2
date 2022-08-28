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
        self.eta = 0.001

        
    def error(self, label):
        score = self.base.score(label)
        return (score < self.threshold).astype('float')
    

    def update(self, label):
        
        score = self.base.score(label)
        assert(not np.isnan(score))
        err = (score < self.threshold).astype('float')
        self.threshold = self.threshold + self.eta*(self.args.alpha - err)
        self.threshold = max(self.args.threshold_min, self.threshold)
        self.threshold = min(self.args.threshold_max, self.threshold)

        
    def predict(self):
        interval = self.base.superlevelset(self.threshold)
        return interval
    

                
        

        
