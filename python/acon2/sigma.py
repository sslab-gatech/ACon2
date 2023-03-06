import os, sys
import warnings
import numpy as np

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
        obs_pred = self.base.predict()
        mu, sig = np.squeeze(obs_pred['mu']), np.sqrt(np.squeeze(obs_pred['cov']))
        interval = [mu - sig, mu + sig]
        return interval

    
    def init_or_update(self, label):
        
        if label is None:
            return

        if not self.initialized:
            self.base.init_state(label)
            self.initialized = True
        else:
            
            # check error before update
            err = self.error(label)
            self.n_err += err
            self.n_obs += 1
            # print(f'MVP: error = {self.n_err}, n = {self.n_obs}')
            
            # predict
            self.ps = self.predict()            
            
            print(f'[OneSigma] size = {self.ps[1] - self.ps[0]:.4f}, '
                  f'interval = [{self.ps[0]:.4f}, {self.ps[1]:.4f}], obs = {label:.4f}, '
                  f'error_cur = {err}, '
                  f'error = {self.n_err / self.n_obs:.4f}'
            )

            # update the base model
            self.base_out = self.base.update(label, update_max=False)
            self.label = label

            
    def summary(self):
        return {
            'obs': self.label,
            'ps': self.ps,
            'n_err': self.n_err,
            'n_obs': self.n_obs,
        }
