import os, sys
import numpy as np


class ACon2:
    def __init__(self, args, models):
        self.args = args
        self.models = models
        self.reset()

        
    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.ps = None

        
    @ property
    def initialized(self):
        return all([self.models[k].initialized for k in self.models.keys()])

        
    def error(self, label):
        # assume that the median is the consensued value for our evaluation purpose
        label_c = np.median([label[k] for k in label.keys() if label[k] is not None])

        itv, _ = self.predict()
        if itv[0] <= label_c and label_c <= itv[1]:
            return 0.0
        else:
            return 1.0

        
    def predict(self):
        ps = []
        bps = {}
        for k in self.models.keys():
            ps_k = self.models[k].predict()
            
            # add irreducible error
            if not any(np.isinf(np.abs(ps_k))):
                m = np.mean(ps_k)
                d = m - ps_k[0]
                d += self.args.nonconsensus_param
                ps_k = [m-d, m+d]

            bps[k] = ps_k
            if all(np.isnan(ps_k) == False):
                ps.append(ps_k)

        if len(ps) - self.args.beta <= 0:
            return [-np.inf, np.inf], bps
        else:
            # vote
            edges = [p_i for p in ps for p_i in p]
            edges_vote = [0]*len(edges)
            for i, e in enumerate(edges):
                for ps_i in ps:
                    if ps_i[0] <= e and e <= ps_i[1]:
                        edges_vote[i] += 1

            # interval
            lower = np.inf
            upper = -np.inf

            for e, v in zip(edges, edges_vote):
                if v >= len(ps) - self.args.beta:
                    if lower >= e:
                        lower = e
                    if upper <= e:
                        upper = e

            if lower > upper:
                lower, upper = upper, lower

            # return invalid inf interval if we cannot make consensus
            if lower == -np.inf: 
                lower = np.inf
            if upper == np.inf:
                upper = -np.inf
            
            return [lower, upper], bps
        
            
    def init_or_update(self, label):
            
        if self.initialized:
            # check error
            err = self.error(label)
            self.n_err += err
            self.n_obs += 1
            self.ps, self.bps = self.predict()

        # init or update
        for k in label.keys():
            self.models[k].init_or_update(label[k])
            
            
    def summary(self):
        return {
            'ps': self.ps,
            'ps_updated': self.predict()[0],
            'base_ps': self.bps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
            'n_err_base': {k: self.models[k].n_err for k in self.models.keys()},
            'n_obs_base': {k: self.models[k].n_obs for k in self.models.keys()},
            'alpha': self.args.alpha,
            'beta': self.args.beta,
            'K': len(self.models),
        }
