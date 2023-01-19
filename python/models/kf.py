import os, sys
import warnings
from scipy.stats import norm

import torch as tc
import numpy as np

"""
1D Kalman Filter
"""
class KF1D(tc.nn.Module):
    def __init__(self, args):
        super().__init__()
        print(args)
        self.args = args
        self.dim = 1
        self.state_noise = tc.nn.Parameter(tc.ones(self.dim, self.dim)*args.state_noise_init)
        self.obs_noise = tc.nn.Parameter(tc.ones(self.dim, self.dim)*args.obs_noise_init)
        self.trans_model = tc.tensor([[1.0]])
        self.obs_model = tc.tensor([[1.0]])
        self.score_max = args.score_max

        self.opt = tc.optim.SGD([self.state_noise, self.obs_noise], lr=args.lr)


    def encode(self, obs):
        return tc.ones(self.dim, self.dim)*obs
    
        
    def init_state(self, obs):
        self.state_mu = self.encode(obs)
        self.state_cov = tc.ones(self.dim, self.dim)
        
        
    def predict_nextstate(self):
        state_mu_pred = self.trans_model * self.state_mu.detach()
        state_cov_pred = self.trans_model * self.state_cov.detach() * self.trans_model.t() + tc.exp(self.state_noise) #self.state_noise #tc.exp(self.state_noise)

        # print(f'[KF, pred] mu = {state_mu_pred.item():.4f}, sig = {state_cov_pred.sqrt().item():.4f}')

        return {'mu': state_mu_pred, 'cov': state_cov_pred}

    
    def predict(self):
        state_pred = self.predict_nextstate()
        
        state_mu_pred = state_pred['mu'].detach()
        state_cov_pred = state_pred['cov'].detach()
        
        obs_mu_pred = state_mu_pred
        obs_cov_pred = state_cov_pred + tc.exp(self.obs_noise)
        
        return {'mu': obs_mu_pred, 'cov': obs_cov_pred}

    
    def update(self, state_pred, obs):
        obs = self.encode(obs)
        assert(obs.shape == tc.Size([self.dim, self.dim]))

        # state prediction
        state_mu_pred, state_cov_pred = state_pred['mu'], state_pred['cov']

        # update a state
        obs_inno = obs - self.obs_model * state_mu_pred
        cov_inno = self.obs_model * state_cov_pred * self.obs_model.t() + tc.exp(self.obs_noise) #self.obs_noise #tc.exp(self.obs_noise)
        opt_kalman_gain = state_cov_pred * self.obs_model.t() * tc.inverse(cov_inno)

        self.state_mu = state_mu_pred + opt_kalman_gain * obs_inno
        self.state_cov = (tc.eye(self.dim, self.dim) - opt_kalman_gain * self.obs_model) * state_cov_pred

        # update noise parameters
        self.opt.zero_grad()
        # the negative likelihood of CX + w on an observation, where C = [[1]] is the observation matrix, X is the state, and w is the observation noise
        loss = - tc.distributions.normal.Normal(self.state_mu, (tc.exp(self.state_cov) + tc.exp(self.obs_noise)).sqrt()).log_prob(obs)
        loss.backward(retain_graph=True)
        self.opt.step()

        return {'mu': self.state_mu, 'cov': self.state_cov}

    
    def forward(self, obs):

        # prediction step
        state_pred = self.predict_nextstate()
        
        # update step
        state_updated = self.update(state_pred, obs)
        
        return state_updated

    
    def score(self, obs):
        obs = self.encode(obs)
        # score on the predicted state
        state_pred = self.predict_nextstate()
        score = norm.pdf(obs.item(), loc=state_pred['mu'].item(), scale=(state_pred['cov'] + tc.exp(self.obs_noise)).sqrt().item())
        score = score / self.score_max
        return score


    def superlevelset(self, t):
        warnings.warn('I need a super-level set over an observation distribution')
        t = t * self.score_max
        obs_pred = self.predict()
        if hasattr(t, 'item'):
            t = t.item()
        # if t == 0:
        #     interval = [-np.inf, np.inf]
        #     return interval
        
        mu = obs_pred['mu'].item()
        sig = obs_pred['cov'].sqrt().item()
        c = - 2 * np.log(t + 1e-32) - 2 * np.log(sig + 1e-32) - np.log(2*np.pi)  # avoid numerical error
        c = max(0, c) # an empty prediction set
        interval = [mu - sig * np.sqrt(c), mu + sig * np.sqrt(c)]
        assert not any(np.isnan(interval)), f't = {t}, mu = {mu}, sig = {sig}, c = {c}'
        return interval
