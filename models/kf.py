import os, sys
import warnings
from scipy.stats import norm

import torch as tc
import numpy as np

"""
1D Kalman Filter
"""
class KF1D(tc.nn.Module):
    def __init__(self, state_noise_init=0.1, obs_noise_init=0.1):
        super().__init__()
        
        self.dim = 1
        self.state_mu = tc.nn.Parameter(tc.zeros(self.dim, self.dim), requires_grad=False)
        self.state_cov = tc.nn.Parameter(tc.ones(self.dim, self.dim), requires_grad=False)
        
        self.state_noise = tc.nn.Parameter(tc.ones(self.dim, self.dim)*state_noise_init, requires_grad=True)
        self.obs_noise = tc.nn.Parameter(tc.ones(self.dim, self.dim)*obs_noise_init, requires_grad=True)
        self.trans_model = tc.tensor([[1.0]])
        self.obs_model = tc.tensor([[1.0]])


    def predict(self):
        state_mu_pred = self.trans_model * self.state_mu
        state_cov_pred = self.trans_model * self.state_cov * self.trans_model.t() + self.state_noise
        return {'mu': state_mu_pred, 'cov': state_cov_pred}


    def update(self, state_pred, obs):
        assert(obs.shape == tc.Size([self.dim, self.dim]))

        state_mu_pred, state_cov_pred = state_pred['mu'], state_pred['cov']

        # update step
        obs_inno = obs - self.obs_model * state_mu_pred
        cov_inno = self.obs_model * state_cov_pred * self.obs_model.t() + self.obs_noise
        opt_kalman_gain = state_cov_pred * self.obs_model.t() * tc.inverse(cov_inno)

        self.state_mu.data = state_mu_pred + opt_kalman_gain * obs_inno
        self.state_cov.data = (tc.eye(self.dim, self.dim) - opt_kalman_gain * self.obs_model) * state_cov_pred

        return {'mu': self.state_mu, 'cov': self.state_cov}

    
    def forward(self, obs):

        # prediction step
        state_pred = self.predict()
        
        # update step
        state_updated = self.update(state_pred, obs)
        
        return state_updated

    
    def score(self, obs):
        # score on the predicted state
        state_pred = self.predict()
        score = norm.pdf(obs.item(), loc=state_pred['mu'].item(), scale=state_pred['cov'].sqrt().item())

        return score


    def superlevelset(self, t):
        state_pred = self.predict()
        t = t.item()
        mu = state_pred['mu'].item()
        sig = state_pred['cov'].sqrt().item()
        c = - 2 * np.log(t) - 2 * np.log(sig) - np.log(2*np.pi)
        interval = [mu - sig * np.sqrt(c), mu + sig * np.sqrt(c)]
        return interval
