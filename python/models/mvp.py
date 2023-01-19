import os, sys
import warnings
import numpy as np
from scipy.stats import multinomial

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import logsumexp

# class MultiValidPrediction:
#     def __init__(self, delta=0.1, n_buckets=50, groups=[(lambda x : True)], eta=0.5, r=1000, normalize_by_counts=True):
#         # coverage parameter, want to be 1 - delta covered
#         self.delta = delta
#         # how many buckets do you want?
#         self.n_buckets = n_buckets
#         # groups, given as a collection of True/False outputting functions
#         self.groups = groups
#         self.n_groups = len(groups)
#         # eta, should be set externally based on n_groups, n_buckets, and T
#         self.eta = eta
#         # nuisance parameter
#         self.r = r
#         # do you normalize computation by bucket-group counts? 
#         self.normalize_by_counts = normalize_by_counts

#         # actual thresholds played
#         self.thresholds = []
#         # scores encountered
#         self.scores = []
#         # feature vectors encountered
#         self.xs = []

#         # for each round: 1 = miscovered, 0 = covered
#         self.err_seq = []
#         # vvals[i][g] = v_value on bucket i and group g so far
#         self.vvals = np.zeros((self.n_buckets, self.n_groups), dtype=np.float64)
#         # bg_miscoverage[i][g] = how many times was (i, g) miscovered so far?
#         self.bg_miscoverage = np.zeros((self.n_buckets, self.n_groups), dtype=int)
#         # bg_counts[i][g] = how many times did (i, g) come up so far?
#         self.bg_counts = np.zeros((self.n_buckets, self.n_groups), dtype=int)


#     def predict(self, x):
#         curr_groups = [i for i in range(self.n_groups) if (self.groups[i])(x)]
#         if len(curr_groups) == 0: # arbitrarily return threshold 0 for points with zero groups
#           return 0

#         all_c_neg = True # are all c values nonpositive?
#         cmps_prev = 0.0
#         cmps_curr = 0.0
#         overcalibr_log_prev = 0.0
#         overcalibr_log_curr = 0.0

#         for i in range(self.n_buckets):
#             # compute normalized bucket-group counts
#             norm_fn = lambda x: np.sqrt((x+1)*(np.log2(x+2)**2))
#             bg_counts_norm = 1./norm_fn(self.bg_counts[i, curr_groups])
            
#             # compute sign of cvalue for bucket i
#             a = self.eta * self.vvals[i, curr_groups]
#             if self.normalize_by_counts:
#                 a *= bg_counts_norm
#             mx = np.max(a)
#             mn = np.min(a)

#             if self.normalize_by_counts:
#                 overcalibr_log_curr  =  mx + logsumexp( a - mx, b=bg_counts_norm)
#                 undercalibr_log_curr = -mn + logsumexp(-a + mn, b=bg_counts_norm)
#             else:
#                 overcalibr_log_curr  =  mx + logsumexp( a - mx)
#                 undercalibr_log_curr = -mn + logsumexp(-a + mn)
#             cmps_curr = overcalibr_log_curr - undercalibr_log_curr

#             if cmps_curr > 0:
#                 all_c_neg = False
            
#             if (i != 0) and ((cmps_curr >= 0 and cmps_prev <= 0) or (cmps_curr <= 0 and cmps_prev >= 0)):
#                 cvalue_prev = np.exp(overcalibr_log_prev) - np.exp(undercalibr_log_prev)
#                 cvalue_curr = np.exp(overcalibr_log_curr) - np.exp(undercalibr_log_curr)

#                 Z = np.abs(cvalue_prev) + np.abs(cvalue_curr)
#                 prob_prev = 1 if Z == 0 else np.abs(cvalue_curr)/Z
#                 if np.random.random_sample() <= prob_prev:
#                     return (1.0 * i) / self.n_buckets - 1.0 /(self.r * self.n_buckets)
#                 else:
#                     return 1.0 * i / self.n_buckets

#             cmps_prev = cmps_curr
#             overcalibr_log_prev = overcalibr_log_curr
#             undercalibr_log_prev = undercalibr_log_curr

#         return (1.0 if all_c_neg else 0.0)

#     def update(self, x, threshold, score):
#         curr_groups = [i for i in range(self.n_groups) if (self.groups[i])(x)]
#         if len(curr_groups) == 0: # don't update on points with zero groups
#           return

#         self.thresholds.append(threshold)
#         self.scores.append(score)
#         self.xs.append(x)

#         bucket = min(int(threshold * self.n_buckets + 0.5/self.r), self.n_buckets - 1)
#         err_ind = int(score > threshold)
      
#         # update vvals
#         self.vvals[bucket, curr_groups] += self.delta - err_ind # (1-err_ind) - (1-delta)
#         # update stats
#         self.bg_counts[bucket, curr_groups] += 1
#         self.bg_miscoverage[bucket, curr_groups] += err_ind
#         self.err_seq.append(err_ind)

#     def coverage_stats(self, plot_thresholds=True, print_per_group_stats=True):
#         if plot_thresholds:
#           plt.plot(self.thresholds)
#           plt.title('Thresholds')
#           plt.show()

#         if print_per_group_stats:
#           print('Per-Group Coverage Statistics:')
#           for group in range(self.n_groups):
#               miscoverages = np.sum(self.bg_miscoverage[:, group])
#               counts = np.sum(self.bg_counts[:, group])
#               miscoverage_rate = miscoverages/counts

#               spacing = int(np.ceil(np.log10(len(self.thresholds))))
#               group_spacing = int(np.ceil(np.log10(self.n_groups)))
#               print(  'Group ',         '{:{x}d}'.format(group, x=group_spacing), 
#                     ': Count: ',        '{:{x}d}'.format(counts, x=spacing), 
#                     ', Miscoverages: ', '{:{x}d}'.format(miscoverages, x=spacing), 
#                     ', Rate: ',         f'{miscoverage_rate:.6f}')
        
#         return self.thresholds, self.bg_miscoverage, self.bg_counts


# class MVP:
#     def __init__(self, args, model_base):
#         super().__init__()
#         self.args = args
#         self.base = model_base

#         self.reset()
#         self.mvp = MultiValidPrediction(delta=args.alpha, n_buckets=200, eta=args.eta) ##TODO

        
#     def reset(self):
#         self.n_err = 0
#         self.n_obs = 0
#         self.initialized = False
#         self.ps = None
#         self.updated = False
        
        
#     def error(self, label):
#         score = self.base.score(label)
#         return (score < self.threshold).astype('float')

    
#     def predict(self):
#         interval = self.base.superlevelset(self.threshold)
#         return interval

    
#     def update(self, label):
        
#         if label is None:
#             return

#         if not self.initialized:
#             self.base.init_state(label)
#             self.initialized = True
#             self.threshold = 0 ##TODO
#         else:
            
#             ##original MVP
#             score = 1 - self.base.score(label)
            
#             self.threshold = self.mvp.predict(None)
#             self.ps = self.predict()
#             self.mvp.update(label, self.threshold, score)

#             # update the base model
#             self.base_out = self.base(label)


#             # print('threshold =', 1 - self.threshold, 'score =', 1 - score, f'interval = [{self.ps[0]}, {self.ps[1]}]')
#             self.n_err = np.sum(self.mvp.bg_miscoverage)
#             self.n_obs += 1
#             self.label = label
#             self.updated = True

#             self.mvp.coverage_stats(plot_thresholds=False)

            
#             # print('miscoverage =', self.n_err / self.n_obs)
            
#     def summary(self):
#         return {
#             'obs': self.label,
#             'ps': self.ps,
#             'n_err': self.n_err,
#             'n_obs': self.n_obs,
#         }

    
# class MVPSimple:
#     def __init__(self, args, model_base):
#         super().__init__()
#         self.args = args
#         self.base = model_base
#         # self.threshold_min = self.args.threshold_min
#         # self.threshold_max = self.args.threshold_max
#         self.eta = self.args.eta
#         self.threshold = 0 #TODO: dummy; remove
#         self.n_bins = self.args.n_bins
#         self.r = 1000 # not sensitiy on results
#         self.e = 1.0 # not sensitiy on results
#         self.reset()


#     def reset(self):
#         self.n_err = 0
#         self.n_obs = 0
#         self.initialized = False
#         self.ps = None
#         # self.updated = False

#         self.thres_cnt = np.zeros(self.n_bins)
#         self.corr_cnt = np.zeros(self.n_bins)
#         self.norm_func = lambda n: np.sqrt((n+1) * np.power(np.log(n+2), 1 + self.e))
        
        
#     def error(self, label):
#         score = self.base.score(label)
#         # print(f'score = {score}, label = {label}, threshold = {self.threshold}')
#         if score >= 1.0:
#             warnings.warn(f'score is larger than one: score = {score}')
#         return (score < self.threshold).astype('float')

    
#     def predict(self):
#         interval = self.base.superlevelset(self.threshold)
#         # print(f'verify interval = {self.error(interval[0]+1e-3)}, {self.error(np.mean(interval))}, {self.error(interval[1]-1e-3)}')
#         return interval

    
#     def init_or_update(self, label):
        
#         if label is None:
#             return

#         def find_threshold_mvp():
            
#             all_c_neg = True # are all c values nonpositive?
#             cmps_prev = 0.0
#             cmps_curr = 0.0
#             overcalibr_log_prev = 0.0
#             overcalibr_log_curr = 0.0

#             for i in range(self.n_bins):
#                 # compute normalized bucket-group counts
#                 norm_fn = lambda x: np.sqrt((x+1)*(np.log2(x+2)**2))
#                 bg_counts_norm = 1./norm_fn(self.thres_cnt[i])

#                 # compute sign of cvalue for bucket i
#                 a = self.eta * self.corr_cnt[i] * bg_counts_norm

#                 overcalibr_log_curr  =  a
#                 undercalibr_log_curr = -a
                
#                 # mx = np.max(a)
#                 # mn = np.min(a)

#                 # overcalibr_log_curr  =  mx + logsumexp( a - mx, b=bg_counts_norm)
#                 # undercalibr_log_curr = -mn + logsumexp(-a + mn, b=bg_counts_norm)
                    
#                 cmps_curr = overcalibr_log_curr - undercalibr_log_curr

#                 if cmps_curr > 0:
#                     all_c_neg = False

#                 if (i != 0) and ((cmps_curr >= 0 and cmps_prev <= 0) or (cmps_curr <= 0 and cmps_prev >= 0)):
#                     cvalue_prev = np.exp(overcalibr_log_prev) - np.exp(undercalibr_log_prev)
#                     cvalue_curr = np.exp(overcalibr_log_curr) - np.exp(undercalibr_log_curr)

#                     Z = np.abs(cvalue_prev) + np.abs(cvalue_curr)
#                     prob_prev = 1 if Z == 0 else np.abs(cvalue_curr)/Z
#                     if np.random.random_sample() <= prob_prev:
#                         thres = (1.0 * i) / self.n_bins - 1.0 /(self.r * self.n_bins)
#                         return thres
#                     else:
#                         thres = 1.0 * i / self.n_bins
#                         return thres

#                 cmps_prev = cmps_curr
#                 overcalibr_log_prev = overcalibr_log_curr
#                 undercalibr_log_prev = undercalibr_log_curr

#             return (1.0 if all_c_neg else 0.0)


#         def find_threshold_mvp_custom():
#             # update
#             weights = np.exp(self.eta * self.corr_cnt / self.norm_func(self.thres_cnt))
#             weights -= np.exp(-self.eta * self.corr_cnt / self.norm_func(self.thres_cnt))
#             weights /= self.norm_func(self.thres_cnt)
            
#             if all(weights > 0):
#                 threshold = 1.0 #TODO
#             elif all(weights < 0):
#                 threshold = 0.0 #TODO
#             else:
#                 i_star = None
#                 for i in range(1, self.n_bins-1):
#                     if weights[i-1] * weights[i] <= 0:
#                         i_star = i
#                         break
#                 assert(i_star is not None)
#                 Z = np.abs(weights[i_star-1]) + np.abs(weights[i_star])
#                 p_t = 1 if Z == 0 else np.abs(weights[i_star-1]) / Z

#                 # choose the aggressive threshold
#                 if np.random.rand() <= p_t:
#                     # more aggressive
#                     threshold = i_star / self.n_bins
#                 else:
#                     threshold = i_star / self.n_bins - 1 / (self.n_bins + self.r) #TODO
                    
#             return threshold

#         # def find_threshold_mvp():
#         #     # update
#         #     weights = np.exp(self.eta * self.corr_cnt / self.norm_func(self.thres_cnt))
#         #     weights -= np.exp(-self.eta * self.corr_cnt / self.norm_func(self.thres_cnt))
#         #     weights /= self.norm_func(self.thres_cnt)
            
#         #     if all(weights > 0):
#         #         threshold = 1.0 #TODO
#         #     elif all(weights < 0):
#         #         threshold = 0.0 #TODO
#         #     else:
#         #         i_star = None
#         #         for i in range(1, self.n_bins):
#         #             if weights[i-1] * weights[i] <= 0:
#         #                 i_star = i
#         #                 break
#         #         assert(i_star is not None)
#         #         Z = np.abs(weights[i_star-1]) + np.abs(weights[i_star])
#         #         p_t = 1 if Z == 0 else np.abs(weights[i_star]) / Z
                
#         #         if np.random.rand() <= p_t:
#         #             threshold = i_star / self.n_bins - 1 / (self.n_bins + self.r) #TODO
#         #         else:
#         #             threshold = i_star / self.n_bins
                    
#         #     return threshold

#         if not self.initialized:
#             self.base.init_state(label)
#             self.initialized = True
#             self.threshold = 1.0 - find_threshold_mvp()
#         else:
            
#             # check error before update
#             err = self.error(label)
#             self.n_err += err
#             self.n_obs += 1
            
#             # predict
#             self.ps = self.predict()            
            
#             # update stats
#             bin_idx = min(int((1.0 - self.threshold) * self.n_bins + 0.5/self.r), self.n_bins - 1)
#             self.thres_cnt[bin_idx] += 1
#             self.corr_cnt[bin_idx] += self.args.alpha - err #TODO

#             # update a threshold
#             self.threshold = 1.0 - find_threshold_mvp()

#             # print(f'threshold = {self.threshold:.4f}, size = {self.ps[1] - self.ps[0]:.4f}, interval = [{self.ps[0]:.4f}, {self.ps[1]:.4f}]')


#             # update the base model
#             self.base_out = self.base(label)

#             self.label = label
#             # self.updated = True
            
#             # print(f'miscoverage = {self.n_err / self.n_obs:.4f}')
            
#     def summary(self):
#         return {
#             'obs': self.label,
#             'ps': self.ps,
#             'n_err': self.n_err,
#             'n_obs': self.n_obs,
#         }


class SpecialMVP:
    def __init__(self, args, model_base):
        super().__init__()
        self.args = args
        self.base = model_base
        self.eta = self.args.eta
        # self.threshold = 0
        # self.threshold = 1
        self.n_bins = self.args.n_bins
        self.r = 1000 # not sensitiy on results
        self.e = 1.0 # not sensitiy on results
        self.reset()


    def reset(self):
        self.n_err = 0
        self.n_obs = 0
        self.initialized = False
        self.ps = None
        # self.updated = False

        self.thres_cnt = np.zeros(self.n_bins)
        self.corr_cnt = np.zeros(self.n_bins)
        assert(self.e == 1)
        #self.norm_func = lambda n: np.sqrt((n+1) * np.power(np.log2(n+2), 1 + self.e))
        self.norm_func = lambda n: np.sqrt((n+1) * (np.log2(n+2)**2))
        
        
    def error(self, label):
        score = self.base.score(label)
        # print(f'score = {score}, label = {label}, threshold = {self.threshold}')
        if score >= 1.0:
            warnings.warn(f'score is larger than one: score = {score}')
        return (score < self.threshold).astype('float')

        # itv = self.predict()
        # if itv[0] <= label and label <= itv[1]:
        #     return 0.0
        # else:
        #     return 1.0


    
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
                        thres = (1.0 * i) / self.n_bins - 1.0 /(self.r * self.n_bins)
                        # return thres
                        return 1 - thres
                    else:
                        thres = (1.0 * i) / self.n_bins
                        # return thres
                        return 1 - thres
                    
                w_prev = w_cur
                
            if pos:
                return 1.0
            else:
                return 0.0
            # if pos:
            #     return 0.0
            # else:
            #     return 1.0


        if not self.initialized:
            self.base.init_state(label)
            self.initialized = True
            self.threshold = find_threshold_mvp()
            # self.threshold = 1 - find_threshold_mvp()
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
            
            print(self.threshold)

            
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
