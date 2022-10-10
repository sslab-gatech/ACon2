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

    
    # @ property
    # def updated(self):
    #     return all([self.models[k].updated for k in self.models.keys()])

    
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

    
    
    
    # def predict(self, search_step=1e-4):
    #     # assume an interval; over-approximate the final interval
    #     ps = [self.models[k].predict() for k in self.models.keys()]
    #     print(ps)
        
    #     ps_lower = sorted([p[0] for p in ps])
    #     ps_upper = sorted([p[1] for p in ps])

    #     p_lower_out = -np.inf
    #     for p_lower in ps_lower:
    #         score = np.sum([1.0 - self.models[k].error(p_lower + self.small) for k in self.models.keys()])
            
    #         print(score, len(self.models), self.args.beta)
    #         print('p_lower =', p_lower)
    #         print('should have one =', [1.0 - self.models[k].error(p_lower + 0.001) for k in self.models.keys()])
    #         print('should have one =', [1.0 - self.models[k].error(p_lower + 0.01) for k in self.models.keys()])
    #         print('should have one =', [1.0 - self.models[k].error(p_lower + 0.1) for k in self.models.keys()])

    #         if score >= len(self.models) - self.args.beta:
    #             p_lower_out = p_lower
    #             break
        
    #     p_upper_out = np.inf
    #     for p_upper in reversed(ps_upper):
    #         score = np.sum([1.0 - self.models[k].error(p_upper - self.small) for k in self.models.keys()])
    #         if score >= len(self.models) - self.args.beta:
    #             p_upper_out = p_upper
    #             break
    #     interval = [p_lower_out, p_upper_out]
    #     return interval

    
    # def predict(self, search_step=1e-1):
    #     # assume an interval; over-approximate the final interval
    #     ps = []
    #     keys = []
    #     for k in self.models.keys():
    #         ps_k = self.models[k].predict()
    #         # print(f'{k} = [{ps_k[0]}, {ps_k[1]}]')
    #         if all(np.isnan(ps_k) == False):
    #             ps.append(ps_k)
    #             keys.append(k)
            
    #     if len(ps) == 0:
    #         return [-np.inf, np.inf]
    #     else:
    #         edges = sorted([p_i for p in ps for p_i in p])
    #         ps_candi = []
    #         prev_es = None
    #         prev_d = None
    #         for e1, e2 in zip(edges[:-1], edges[1:]):
    #             score = np.sum([1.0 - self.models[k].error(np.mean([e1, e2])) for k in keys])
    #             if score >= len(ps) - self.args.beta:
    #                 ps_candi.append(np.mean([e1, e2]))

    #             prev_es = [e1, e2]
                    
    #         if len(ps_candi) == 0:
    #             return [-np.inf, np.inf]
    #         else:
    #             return [np.min(ps_candi), np.max(ps_candi)]

            
    #         # ps_lower = np.max([p[0] for p in ps])
    #         # ps_upper = np.min([p[1] for p in ps])
        
    #         # score = np.sum([1.0 - self.models[k].error(np.mean([ps_lower, ps_upper])) for k in self.models.keys()])
    #         # if score >= len(ps) - self.args.beta:
    #         #     return [ps_lower, ps_upper]
    #         # else:
    #         #     return [-np.inf, np.inf]
            
                
    #     # p_lower_out = -np.inf
    #     # if score = np.sum([1.0 - self.models[k].error(p_lower) for k in self.models.keys()])
        
    #     # for p_lower in np.arange(ps_min, ps_max+search_step, search_step):
    #     #     score = np.sum([1.0 - self.models[k].error(p_lower) for k in self.models.keys()])
    #     #     if score >= len(self.models) - self.args.beta:
    #     #         p_lower_out = p_lower
    #     #         break
                    
    #     # p_upper_out = np.inf
    #     # for p_upper in reversed(np.arange(ps_min, ps_max+search_step, search_step)):
    #     #     score = np.sum([1.0 - self.models[k].error(p_upper) for k in self.models.keys()])
    #     #     if score >= len(self.models) - self.args.beta:
    #     #         p_upper_out = p_upper
    #     #         break

        
    def predict(self):
        ps = []
        bps = {}
        for k in self.models.keys():
            ps_k = self.models[k].predict()
            bps[k] = ps_k
            #print(f'{k} = [{ps_k[0]}, {ps_k[1]}]')
            if all(np.isnan(ps_k) == False):
                ps.append(ps_k)
            
        if len(ps) == 0:
            return [-np.inf, np.inf], bps
        else:
            edges = sorted([p_i for p in ps for p_i in p]) #TODO: sorting is not necessary
            edges_vote = [0]*len(edges)
            for i, e in enumerate(edges):
                for ps_i in ps:
                    if ps_i[0] <= e and e <= ps_i[1]:
                        edges_vote[i] += 1
            edges_maj = []
            for i, v in enumerate(edges_vote):
                if v >= len(ps) - self.args.beta:
                    edges_maj.append(edges[i])
            if len(edges_maj) == 0:
                return [-np.inf, np.inf], bps
            else:
                return [np.min(edges_maj), np.max(edges_maj)], bps

            
    def init_or_update(self, label):

        if self.initialized:
            # check error
            self.n_err += self.error(label)
            self.n_obs += 1
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
