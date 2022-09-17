import os, sys
import argparse
import torch as tc
import copy
import warnings

import data
import utils
import models

import numpy as np

def parse_args():
    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')

    ## meta args
    parser.add_argument('--exp_name', type=str, required=True)
    parser.add_argument('--output_root', type=str, default='output')
    parser.add_argument('--cpu', action='store_true')

    ## data args
    parser.add_argument('--data.name', type=str, default='PriceDataset')
    parser.add_argument('--data.path', type=str, nargs='+', default=[
        'data/price_USD_ETH/coinbase',
        'data/price_USD_ETH/binance',
        'data/price_USD_ETH/UniswapV2',
    ])    
    #parser.add_argument('--data.path', type=str, default='data/price_ETH_USD/coinbase')    
    # parser.add_argument('--data.batch_size', type=int, default=1)
    # parser.add_argument('--data.n_workers', type=int, default=0)
    parser.add_argument('--data.seed', type=lambda v: None if v=='None' else int(v), default=0)

    ## model args
    parser.add_argument('--model_base.name', type=str, nargs='+', default=['KF1D', 'KF1D', 'KF1D'])
    parser.add_argument('--model_base.score_min', type=float, nargs='+', default=[0.0, 0.0, 0.0])
    parser.add_argument('--model_base.score_max', type=float, nargs='+', default=[1.0, 1.0, 1.0])
    parser.add_argument('--model_base.lr', type=float, nargs='+', default=[1e-3, 1e-3, 1e-3])
    parser.add_argument('--model_base.state_noise_init', type=float, nargs='+', default=[1.0, 1.0, 1.0])
    parser.add_argument('--model_base.obs_noise_init', type=float, nargs='+', default=[1.0, 1.0, 1.0])
    
    parser.add_argument('--model_ps.name', type=str, nargs='+', default=['MVPSimple', 'MVPSimple', 'MVPSimple'])    
    # parser.add_argument('--model_ps.threshold_min', type=float, nargs='+', default=[0.0, 0.0, 0.0])
    # parser.add_argument('--model_ps.threshold_max', type=float, nargs='+', default=[1.0, 1.0, 1.0])
    # parser.add_argument('--model_ps.threshold_step', type=float, nargs='+', default=[0.01, 0.01, 0.00])
    parser.add_argument('--model_ps.n_bins', type=int, nargs='+', default=[100, 100, 100])
    
    parser.add_argument('--model_ps.eta', type=float, default=0.9)
    parser.add_argument('--model_ps.alpha', type=float, nargs='+', default=[0.01, 0.01, 0.01])
    parser.add_argument('--model_ps.beta', type=int, default=1) 
    #parser.add_argument('--model_ps.T', type=int, default=50000)
    

    ## training algorithm args
    parser.add_argument('--train.method', type=str, default='skip')
    

    args = parser.parse_args()
    args = utils.to_tree_namespace(args)
    args.device = tc.device('cpu') if args.cpu else tc.device('cuda:0')
    args = utils.propagate_args(args, 'device')
    args = utils.propagate_args(args, 'exp_name')
    args = utils.propagate_args(args, 'output_root')
    
    ## set loggers
    os.makedirs(os.path.join(args.output_root, args.exp_name), exist_ok=True)
    sys.stdout = utils.Logger(os.path.join(args.output_root, args.exp_name, 'out'))
    
    ## print args
    utils.print_args(args)
    
    return args    


def split_args(args):
    args_split = []
    for i in range(len(args.name)):
        args_new = copy.deepcopy(args)
        for d in args.__dict__:
            if type(getattr(args, d)) == list:
                setattr(args_new, d, getattr(args, d)[i])
        args_split.append(args_new)
    return args_split
    

# def run1(args):

#     ## load a dataset
#     ds = getattr(data, args.data.name)(args.data.path)
    
#     ## load a base model
#     #model_base = getattr(models, args.model_base.name)(state_noise_init=np.log(10), obs_noise_init=np.log(10))
#     model_base = getattr(models, args.model_base.name)(args.model_base)

#     ## load a prediction set
#     model_ps = getattr(models, args.model_ps.name)(args.model_ps, model_base)
#     model_cs = models.ACC(model_base)

#     ## prediction
#     n_err = 0
#     results = []
#     results_fn = os.path.join(args.output_root, args.exp_name, '_'.join(args.data.path.split('/')[1:]), args.model_ps.name, 'results.pk')
    
    
#     for t, (timestamp, obs) in enumerate(ds.seq):
        
#         time = np.array(timestamp.item()).astype('datetime64[s]')
#         obs = obs.unsqueeze(0)
#         if t == 0:
#             model_ps.base.init_state(obs)
#         else:
#             # measure the performance
#             n_err += model_ps.error(obs)
#             ps = model_ps.predict()

#             # update thresholds        
#             model_ps.update(obs)

#             # update the KF state
#             state_est = model_ps.base(obs)

#             print(f"[time = {time}] obs = {obs.item()}, mu = {state_est['mu'].item():.2f}, cov = {state_est['cov'].item():.4f}, "\
#                   f"threshold = {model_ps.threshold:.4f}, interval = [{ps[0]:.2f}, {ps[1]:.2f}], length = {ps[1] - ps[0]:.2f}, error = {n_err / t}")

#             results.append({'time': time, 'obs': obs, 'pred_set': ps, 'error': n_err / t})
#             if t >= args.model_ps.T:
#                 break

#     os.makedirs(os.path.dirname(results_fn), exist_ok=True)
#     import pickle
#     pickle.dump({'predictions': results, 'args': args}, open(results_fn, 'wb'))


class Clock:
    def __init__(self, time_start, time_end, delta_sec):
        self.time_start = time_start
        self.time_end = time_end
        self.delta_sec = delta_sec


    def __iter__(self):
        self.time = self.time_start
        return self

    def __next__(self):
        if self.time.astype('datetime64[s]') > self.time_end.astype('datetime64[s]'):
            raise StopIteration
        time = self.time
        self.time += self.delta_sec
        return time
        

# def run_indep(args):

#     ## load a dataset
#     ds = getattr(data, args.data.name)(args.data.path)

#     ## load a base model
#     model_base = {k: getattr(models, v)() for k, v in zip(args.data.path, args.model_base.name)}

#     ## load a prediction set
#     model_ps = {k: getattr(models, model_name)(model_args, model_base[k]) for k, model_name, model_args in zip(args.data.path, args.model_ps.name, split_args(args.model_ps))}

#     ## prediction
#     # n_err = 0
#     results = []
#     results_fn = os.path.join(args.output_root, args.exp_name, 'results.pk')

    
#     for i, time in enumerate(Clock(np.datetime64('2021-01-01T00:00'), np.datetime64('2021-12-31T23:59'), np.timedelta64(30, 's'))):

#         # read observations
#         obs = ds.read(time)

#         # update
#         for k in model_ps.keys():
#             if obs[k] is None:
#                 continue
#             initialized = model_ps[k].initialized
#             model_ps[k].update(None if obs[k] is None else obs[k]['price'])
#             if initialized:
#                 print(f"[time = {time}, {k}] obs = {obs[k]['price']}, mu = {model_ps[k].base_out['mu'].item():.4f}, cov = {model_ps[k].base_out['cov'].item():.4f}, "\
#                       f"threshold = {model_ps[k].threshold:.4f}, interval = [{model_ps[k].ps[0]:.4f}, {model_ps[k].ps[1]:.4f}], length = {model_ps[k].ps[1] - model_ps[k].ps[0]:.4f}, "\
#                       f"error = {model_ps[k].n_err / model_ps[k].n_obs}")
                
#         if all([model_ps[k].updated for k in model_ps.keys()]):        
#             results.append({'time': time, 'prediction': {k: model_ps[k].summary() for k in model_ps.keys()}})

#     # save
#     os.makedirs(os.path.dirname(results_fn), exist_ok=True)
#     import pickle
#     pickle.dump({'predictions': results, 'args': args}, open(results_fn, 'wb'))


def run(args):
    # time_start = np.datetime64('2021-01-01T00:00')
    # time_end = np.datetime64('2021-12-31T23:59')
    # time_delta = np.timedelta64(30, 's')

    time_start = np.datetime64('2022-03-31T00:00')
    time_end = np.datetime64('2022-05-31T23:59')
    time_delta = np.timedelta64(10, 's')
    
    ## load a dataset
    ds = getattr(data, args.data.name)(args.data.path)

    ## load a base model
    model_base = {k: getattr(models, v)(model_base_args) for k, v, model_base_args in zip(args.data.path, args.model_base.name, split_args(args.model_base))}
    
    ## load a prediction set
    model_ps_src = {k: getattr(models, model_name)(model_args, model_base[k]) for k, model_name, model_args in zip(args.data.path, args.model_ps.name, split_args(args.model_ps))}

    model_ps = models.ACC(args.model_ps, model_ps_src)

    ## prediction
    results = []
    outputs_fn = os.path.join(args.output_root, args.exp_name, 'out.pk')

    for i, time in enumerate(Clock(time_start, time_end, time_delta)):
        # read observations
        try: 
            obs = ds.read(time)
        except StopIteration:
            break

        if all([obs[k] is None for k in obs.keys()]):
            continue
            
        
        # update
        if not model_ps.initialized:
            model_ps.init_or_update(obs)
        else:
            model_ps.init_or_update(obs)
            
            print(f"[time = {time}] median(obs) = {np.median([obs[k] for k in obs.keys() if obs[k] is not None]):.4f}, "\
                  f"interval = [{model_ps.ps[0]:.4f}, {model_ps.ps[1]:.4f}], length = {model_ps.ps[1] - model_ps.ps[0]:.4f}, "\
                  f"error = {model_ps.n_err / model_ps.n_obs:.4f}")
            results.append({'time': time, 'prediction_summary': model_ps.summary(), 'observation': obs})

    # save
    os.makedirs(os.path.dirname(outputs_fn), exist_ok=True)
    import pickle
    pickle.dump({'results': results, 'args': args}, open(outputs_fn, 'wb'))

    
if __name__ == '__main__':
    args = parse_args()
    run(args)

