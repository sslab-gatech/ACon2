import os, sys
import warnings
from scipy.stats import norm

import numpy as np

"""
1D Kalman Filter
"""
class KF1D:
    def __init__(self, args):
        super().__init__()
        print(args)
        self.args = args
        self.dim = 1
        self.state_noise_sig_log = np.ones((self.dim, self.dim))*args.state_noise_init
        self.obs_noise_sig_log = np.ones((self.dim, self.dim))*args.obs_noise_init
        self.state_inoise_sig_log = np.ones((self.dim, self.dim))*args.state_noise_init

        self.trans_model = np.array([[1.0]])
        self.obs_model = np.array([[1.0]])
        self.score_max = args.score_max


    def encode(self, obs):
        return np.ones((self.dim, self.dim))*obs
    
        
    def init_state(self, obs):
        self.obs = obs
        self.state_mu = self.encode(obs)
        self.state_cov = np.ones((self.dim, self.dim))
        
        
    def predict_nextstate(self):
        state_mu_pred = self.trans_model * self.state_mu
        state_cov_pred = self.trans_model * self.state_cov * np.transpose(self.trans_model) + np.power(np.exp(self.state_noise_sig_log), 2)

        # print(f'[KF, pred] mu = {state_mu_pred.item():.4f}, sig = {state_cov_pred.sqrt().item():.4f}')

        return {'mu': state_mu_pred, 'cov': state_cov_pred}

    
    def predict(self):
        state_pred = self.predict_nextstate()
        
        state_mu_pred = state_pred['mu']
        state_cov_pred = state_pred['cov']
        
        obs_mu_pred = state_mu_pred
        obs_cov_pred = state_cov_pred + np.power(np.exp(self.obs_noise_sig_log), 2)
        
        return {'mu': obs_mu_pred, 'cov': obs_cov_pred}


    def update_score_max(self):
        pred = self.predict()
        mu = np.squeeze(pred['mu'])
        sig = np.squeeze(np.sqrt(pred['cov']))
        self.score_max = norm.pdf(mu, loc=mu, scale=sig) * 2
        #print(f'score_max = {self.score_max:.4f}, mu = {mu:.4f}, sig = {sig:.4f}')
        
    
    def update_noise(self, obs):
        obs = self.encode(obs)
        assert(obs.shape == (self.dim, self.dim))

        # update noise parameters
        y = obs
        mu = self.state_mu
        cov = self.state_cov
        wbar = self.state_noise_sig_log
        vbar = self.obs_noise_sig_log
        w = np.exp(wbar)
        v = np.exp(vbar)
        xi = np.sqrt(cov + np.power(np.exp(wbar), 2) + np.power(np.exp(vbar), 2))
        diff = y - mu

        grad_state_noise_sig_log = ( 1/xi - np.power(diff, 2)/np.power(xi, 3) ) * ( w/xi ) * np.exp(wbar) 
        grad_obs_noise_sig_log = ( 1/xi - np.power(diff, 2)/np.power(xi, 3) ) * ( v/xi ) * np.exp(vbar)

        self.state_noise_sig_log = self.state_noise_sig_log - self.args.lr * grad_state_noise_sig_log
        self.obs_noise_sig_log = self.obs_noise_sig_log - self.args.lr * grad_obs_noise_sig_log

        # noise clipping
        self.state_noise_sig_log = max(self.state_noise_sig_log, self.state_inoise_sig_log)
        
        
        
    def update_state(self, state_pred, obs):
        obs = self.encode(obs)
        assert(obs.shape == (self.dim, self.dim))

        # state prediction
        state_mu_pred, state_cov_pred = state_pred['mu'], state_pred['cov']

        # update a state
        obs_inno = obs - self.obs_model * state_mu_pred
        cov_inno = self.obs_model * state_cov_pred * np.transpose(self.obs_model) + np.power(np.exp(self.obs_noise_sig_log), 2)
        opt_kalman_gain = state_cov_pred * np.transpose(self.obs_model) * np.linalg.inv(cov_inno)

        self.state_mu = state_mu_pred + opt_kalman_gain * obs_inno
        self.state_cov = (np.eye(self.dim, self.dim) - opt_kalman_gain * self.obs_model) * state_cov_pred
        
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

    
    
    def score(self, obs):
        obs = self.encode(obs)
        # score on the predicted observation
        obs_pred = self.predict()
        assert((obs_pred['mu'].shape == (self.dim, self.dim)) and (obs_pred['cov'].shape == (self.dim, self.dim)))
        score = norm.pdf(np.squeeze(obs), loc=np.squeeze(obs_pred['mu']), scale=np.sqrt(np.squeeze(obs_pred['cov'])))
        score = score / self.score_max
        return score


    def superlevelset(self, t):
        t = t * self.score_max
        obs_pred = self.predict()
            
        if t == 0:
            interval = [-np.inf, np.inf]
            return interval
        
        mu = np.squeeze(obs_pred['mu'])
        sig = np.sqrt(np.squeeze(obs_pred['cov']))
        assert(sig > 0)
        c = - 2*np.log(t) - 2*np.log(sig) - np.log(2*np.pi) + 1e-8 # avoid numerical error
        # an empty prediction set
        if c <= 0:
            # return an invalid interval for the empty set
            interval = [np.inf, -np.inf]            
        else:
            interval = [mu - sig * np.sqrt(c), mu + sig * np.sqrt(c)]
        assert not any(np.isnan(interval)), f't = {t}, mu = {mu}, sig = {sig}, c = {c}'
        return interval
