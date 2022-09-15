import os, sys
import numpy as np


class ACC:
    def __init__(self, args, models):
        self.args = args
        self.models = models
        self.reset()
        self.small = 1e-4

        
    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.ps = None
        self.err_list = []

        
    @ property
    def initialized(self):
        return all([self.models[k].initialized for k in self.models.keys()])

    
    # @ property
    # def updated(self):
    #     return all([self.models[k].updated for k in self.models.keys()])

    
    def error(self, label):
        # assume the median is the consensued value
        label_c = np.median([label[k] for k in label.keys() if label[k] is not None])
        score = int(np.sum([1.0 - self.models[k].error(label_c) for k in label.keys()]))
        return float(score < len(self.models) - self.args.beta)
    
    
    def predict(self):
        # assume an interval; over-approximate the final interval
        ps = [self.models[k].predict() for k in self.models.keys()]
        ps_lower = sorted([p[0] for p in ps])
        ps_upper = sorted([p[1] for p in ps])

        p_lower_out = -np.inf
        for p_lower in ps_lower:
            score = np.sum([1.0 - self.models[k].error(p_lower + self.small) for k in self.models.keys()])
            if score >= len(self.models) - self.args.beta:
                p_lower_out = p_lower
                break

        p_upper_out = np.inf
        for p_upper in reversed(ps_upper):
            score = np.sum([1.0 - self.models[k].error(p_upper - self.small) for k in self.models.keys()])
            if score >= len(self.models) - self.args.beta:
                p_upper_out = p_upper
                break
        interval = [p_lower_out, p_upper_out]
        return interval

    
    def init_or_update(self, label):
        
        # check error
        if self.initialized:
            err = self.error(label)
            self.n_err += err
            self.ps = self.predict()
            self.n_obs += 1
            # self.err_list.append(err)

        # update
        for k in label.keys():
            self.models[k].update(label[k])
            
            
    def summary(self):
        return {
            'ps': self.ps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
        }
