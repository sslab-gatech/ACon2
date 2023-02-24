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

        
    @ property
    def initialized(self):
        return all([self.models[k].initialized for k in self.models.keys()])

        
    def error(self, label):
        # assume the median is the consensued value
        label_c = np.median([label[k] for k in label.keys() if label[k] is not None])

        # score = int(np.sum([1.0 - self.models[k].error(label_c) for k in label.keys()]))
        # return float(score < len(self.models) - self.args.beta)

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
            #     # # handle an invalid interval
            #     # if ps_k[0] > ps_k[1]:
            #     #     ps_k[0] = 0
            #     #     ps_k[1] = 0
            # else:
                
                m = np.mean(ps_k)
                d = m - ps_k[0]
                #d += m * self.args.nonconsensus_param
                d += self.args.nonconsensus_param
                ps_k = [m-d, m+d]


            bps[k] = ps_k
            if all(np.isnan(ps_k) == False):
                ps.append(ps_k)

        if len(ps) - self.args.beta <= 0:
            return [-np.inf, np.inf], bps
        else:
            # vote
            #edges = sorted([p_i for p in ps for p_i in p]) #TODO: sorting is not necessary
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
                    if lower >= e: #TODO
                        lower = e
                    if upper <= e: #TODO
                        upper = e

            if lower > upper:
                lower, upper = upper, lower

            # return invalid inf interval if we cannot make consensus
            if lower == -np.inf: #TODO
                lower = np.inf
            if upper == np.inf:
                upper = -np.inf
            
            return [lower, upper], bps
        
            # edges_maj = []
            # for i, v in enumerate(edges_vote):
            #     if v >= len(ps) - self.args.beta:
            #         edges_maj.append(edges[i])
            # if len(edges_maj) == 0:
            #     return [-np.inf, np.inf], bps
            # else:
            #     return [np.min(edges_maj), np.max(edges_maj)], bps

            
    def init_or_update(self, label):
            
        if self.initialized:
            # check error
            err = self.error(label)
            self.n_err += err
            self.n_obs += 1
            # self.n_obs_all += 1
            # if self.n_obs_all == 100:
            #     self.n_err = err
            #     self.n_obs = 1
            self.ps, self.bps = self.predict()
            # print(f'ACC: error = {self.n_err}, n = {self.n_obs}')

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
