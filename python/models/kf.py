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
        # self.state_noise_sig_log = tc.nn.Parameter(tc.ones(self.dim, self.dim)*args.state_noise_init)
        # self.obs_noise_sig_log = tc.nn.Parameter(tc.ones(self.dim, self.dim)*args.obs_noise_init)
        self.state_noise_sig_log = tc.ones(self.dim, self.dim)*args.state_noise_init
        self.obs_noise_sig_log = tc.ones(self.dim, self.dim)*args.obs_noise_init

        self.trans_model = tc.tensor([[1.0]])
        self.obs_model = tc.tensor([[1.0]])
        self.score_max = args.score_max

        #self.opt = tc.optim.SGD([self.state_noise, self.obs_noise], lr=args.lr)


    def encode(self, obs):
        return tc.ones(self.dim, self.dim)*obs
    
        
    def init_state(self, obs):
        self.obs = obs
        self.state_mu = self.encode(obs)
        self.state_cov = tc.ones(self.dim, self.dim)
        
        
    def predict_nextstate(self):
        state_mu_pred = self.trans_model * self.state_mu.detach()
        state_cov_pred = self.trans_model * self.state_cov.detach() * self.trans_model.t() + tc.exp(self.state_noise_sig_log).pow(2)

        # print(f'[KF, pred] mu = {state_mu_pred.item():.4f}, sig = {state_cov_pred.sqrt().item():.4f}')

        return {'mu': state_mu_pred, 'cov': state_cov_pred}

    
    def predict(self):
        state_pred = self.predict_nextstate()
        
        state_mu_pred = state_pred['mu'].detach()
        state_cov_pred = state_pred['cov'].detach()
        
        obs_mu_pred = state_mu_pred
        obs_cov_pred = state_cov_pred + tc.exp(self.obs_noise_sig_log).pow(2)
        
        return {'mu': obs_mu_pred, 'cov': obs_cov_pred}


    def update_score_max(self):
        pred = self.predict()
        mu = pred['mu'].item()
        sig = pred['cov'].sqrt().item()
        self.score_max = norm.pdf(mu, loc=mu, scale=sig) 
        print(f'score_max = {self.score_max:.4f}, mu = {mu:.4f}, sig = {sig:.4f}')
        
    
    # def update(self, state_pred, obs):
    #     obs = self.encode(obs)
    #     assert(obs.shape == tc.Size([self.dim, self.dim]))

    #     # state prediction
    #     state_mu_pred, state_cov_pred = state_pred['mu'], state_pred['cov']

    #     # update a state
    #     obs_inno = obs - self.obs_model * state_mu_pred
    #     cov_inno = self.obs_model * state_cov_pred * self.obs_model.t() + tc.exp(self.obs_noise) #self.obs_noise #tc.exp(self.obs_noise)
    #     opt_kalman_gain = state_cov_pred * self.obs_model.t() * tc.inverse(cov_inno)

    #     self.state_mu = state_mu_pred + opt_kalman_gain * obs_inno
    #     self.state_cov = (tc.eye(self.dim, self.dim) - opt_kalman_gain * self.obs_model) * state_cov_pred

    #     # update noise parameters
    #     self.opt.zero_grad()
    #     # the negative likelihood of CX + w on an observation, where C = [[1]] is the observation matrix, X is the state, and w is the observation noise
    #     loss = - tc.distributions.normal.Normal(self.state_mu, (tc.exp(self.state_cov) + tc.exp(self.obs_noise)).sqrt()).log_prob(obs)
    #     loss.backward(retain_graph=True)
    #     self.opt.step()
        
        
    #     # update the max score
    #     self.update_score_max()
        
    #     return {'mu': self.state_mu, 'cov': self.state_cov}


    def update_noise(self, obs):
        obs = self.encode(obs)
        assert(obs.shape == tc.Size([self.dim, self.dim]))

        # update noise parameters
        y = obs
        mu = self.state_mu
        cov = self.state_cov
        wbar = self.state_noise_sig_log
        vbar = self.obs_noise_sig_log
        w = wbar.exp()
        v = vbar.exp()
        xi = (cov + wbar.exp().pow(2) + vbar.exp().pow(2)).sqrt()
        diff = y - mu

        grad_state_noise_sig_log = ( 1/xi - diff.pow(2)/xi.pow(3) ) * ( w/xi ) * wbar.exp() 
        grad_obs_noise_sig_log = ( 1/xi - diff.pow(2)/xi.pow(3) ) * ( v/xi ) * vbar.exp()

        self.state_noise_sig_log = self.state_noise_sig_log - self.args.lr * grad_state_noise_sig_log
        self.obs_noise_sig_log = self.obs_noise_sig_log - self.args.lr * grad_obs_noise_sig_log


    # def update_noise_diff(self, obs):
    #     obs = self.encode(obs)
    #     assert(obs.shape == tc.Size([self.dim, self.dim]))

    #     absdiff = abs(obs - self.obs)
    #     self.obs = obs
    #     self.state_noise_sig_log = absdiff.log()
    #     self.obs_noise_sig_log = absdiff.log()
        
        
    def update_state(self, state_pred, obs):
        obs = self.encode(obs)
        assert(obs.shape == tc.Size([self.dim, self.dim]))

        # state prediction
        state_mu_pred, state_cov_pred = state_pred['mu'], state_pred['cov']

        # update a state
        obs_inno = obs - self.obs_model * state_mu_pred
        cov_inno = self.obs_model * state_cov_pred * self.obs_model.t() + tc.exp(self.obs_noise_sig_log).pow(2)
        opt_kalman_gain = state_cov_pred * self.obs_model.t() * tc.inverse(cov_inno)

        self.state_mu = state_mu_pred + opt_kalman_gain * obs_inno
        self.state_cov = (tc.eye(self.dim, self.dim) - opt_kalman_gain * self.obs_model) * state_cov_pred
        
        return {'mu': self.state_mu, 'cov': self.state_cov}


    def update(self, obs, update_noise=True, update_state=True, update_max=True):
        
        # update noise variance
        if update_noise:
            self.update_noise(obs)
        
        # update the current state
        if update_state:
            state_pred = self.predict_nextstate()
            state_updated = self.update_state(state_pred, obs)

        # update the max score
        if update_max:
            self.update_score_max()

    
    # def forward(self, obs):
    #     return self.update(obs)

    
    def score(self, obs):
        obs = self.encode(obs)
        # score on the predicted observation
        obs_pred = self.predict()
        assert((obs_pred['mu'].shape == tc.Size([1, 1])) and (obs_pred['cov'].shape == tc.Size([1, 1])))
        score = norm.pdf(obs.item(), loc=obs_pred['mu'].squeeze(), scale=obs_pred['cov'].sqrt().squeeze())
        score = score / self.score_max
        return score


    def superlevelset(self, t):
        t = t * self.score_max
        obs_pred = self.predict()
        if hasattr(t, 'item'):
            t = t.item()
            
        if t == 0:
            interval = [-np.inf, np.inf]
            return interval
        
        mu = obs_pred['mu'].item()
        sig = obs_pred['cov'].sqrt().item()
        assert(sig > 0)
        c = - 2*np.log(t) - 2*np.log(sig) - np.log(2*np.pi) + 1e-8 # avoid numerical error
        # an empty prediction set
        if c < 0:
            #print(c, t, sig,  norm.pdf(mu, loc=mu, scale=sig))
            interval = [-np.inf, np.inf]
            return interval
        interval = [mu - sig * np.sqrt(c), mu + sig * np.sqrt(c)]
        assert not any(np.isnan(interval)), f't = {t}, mu = {mu}, sig = {sig}, c = {c}'
        return interval
