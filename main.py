import os, sys
import argparse
import torch as tc

import data
import utils
import models

def parse_args():
    ## init a parser
    parser = argparse.ArgumentParser(description='online learning')

    ## meta args
    parser.add_argument('--exp_name', type=str, required=True)
    parser.add_argument('--output_root', type=str, default='output')
    parser.add_argument('--cpu', action='store_true')

    ## data args
    parser.add_argument('--data.name', type=str, default='Price')
    parser.add_argument('--data.path', type=str, default='data/price_ETH_USD/coinbase')    
    parser.add_argument('--data.batch_size', type=int, default=1)
    parser.add_argument('--data.n_workers', type=int, default=0)
    parser.add_argument('--data.seed', type=lambda v: None if v=='None' else int(v), default=0)

    ## model args
    parser.add_argument('--model_base.name', type=str, default='KF1D')
    parser.add_argument('--model_ps.name', type=str, default='EWA1D')
    parser.add_argument('--model_ps.threshold_min', type=float, default=0.0)
    parser.add_argument('--model_ps.threshold_max', type=float, default=10.0)
    parser.add_argument('--model_ps.threshold_step', type=float, default=0.0001)
    parser.add_argument('--model_ps.alpha', type=float, default=0.01)
    parser.add_argument('--model_ps.T', type=int, default=50000)
    

    ## training algorithm args
    parser.add_argument('--train.method', type=str, default='skip')
    
    ## calibration algorithm args
    parser.add_argument('--cal.method', type=str, default='EWA')
    parser.add_argument('--cal.alpha', type=float, default=0.1)
    parser.add_argument('--cal.rerun', action='store_true')
    

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


def run(args):

    ## load a dataset
    ds = getattr(data, args.data.name)(args.data.path)
    
    ## load a base model
    model_base = getattr(models, args.model_base.name)()

    ## load a prediction set
    model_ps = getattr(models, args.model_ps.name)(args.model_ps, model_base)

    ## prediction
    n_err = 0
    for t, (time, obs) in enumerate(ds.seq, 1):
        obs = obs.unsqueeze(0)

        # measure the performance
        n_err += model_ps.error(obs)
        ps = model_ps.predict()

        # update thresholds        
        model_ps.update(obs)

        # update the KF state
        state_est = model_ps.base(obs)
        
        print(f"[step = {time.item()}] obs = {obs.item()}, mu = {state_est['mu'].item():.2f}, cov = {state_est['cov'].item():.4f}, "\
              f"threshold = {model_ps.threshold:.4f}, interval = [{ps[0]:.2f}, {ps[1]:.2f}], length = {ps[1] - ps[0]:.2f}, error = {n_err / t}")

        if t >= args.model_ps.T:
            break
        
if __name__ == '__main__':
    args = parse_args()
    run(args)

