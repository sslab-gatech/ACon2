# ACon&#178;: Adpative Conformal Consensus

ACon&#178; is an adpative conformal consensus algorithm for provable blockchain oracles. 
In particular, ACon&#178; returns a set of labels (e.g., a range of a token price)
that likely contains a true label (e.g., a true token price) under distribution shift and adversarial manipulation. 

For full details on ACon&#178;, please check our paper on 
"[ACon&#178;: Adaptive Conformal Consensus for Provable Blockchain Oracles](https://arxiv.org/abs/2211.09330)," 
published at USENIX Security '23.

The following includes instructions for Artifact Evaluation. 

## Overview

This artifact produces results of Python and Solidity implementation. 

For Python implementation, we follow three steps.
* Installation (5 human-minutes + 5 compute-minutes)
* Run Experiments (0 human-minutes + 32 compute-hours)
* Validate Results (5 human-minutes + 5 compute-minutes)

For Solidity implementation, we also follow three steps.
* Installation (5 human-minutes + 5 compute-minutes)
* Run Experiments (0 human-minutes + 30 compute-hours)
* Validate Results (5 human-minutes + 5 compute-minutes)


## Python Implementation

### Installation (5 human-minutes + 5 compute-minutes)
* Install [Docker](https://www.docker.com/)
* Pull a docker image via `docker pull ghcr.io/sslab-gatech/acon2:latest`
* Clone this repository
* Execute `cd python`

### (Optional) Run Experiments (0 human-minutes + 32 compute-hours)
Reproducing results in our paper requires time. 
For a short running option which uses precomputed results in the docker image, you can skip this step. 

* Execute `./docker_scripts/docker_run_USD_ETH.sh` for results in files, used for reproducing Figure 4, Figure 5, Figure 6(a), and Figure 9. 
* Execute `./docker_scripts/docker_run_INV_ETH.sh` for results in files, used for reproducing Table 1, Figure 7, Figure 8, and Figure 6(b). 


### Validate Results (5 human-minutes + 5 compute-minutes)

* To reproduce Figure 4, Figure 5, and Figure 6(a), execute `./docker_scripts/docker_plot_USD_ETH.sh` or 
execute `./docker_scripts/docker_plot_USD_ETH_precomp.sh` if you wish to use precomputed results for reproducing results.
  * For Figure 4(a), see `output_docker/one_source_USD_ETH_UniswapV2_K_1_beta_0/figs/plot_ps.pdf`
  * For Figure 4(b), see `output_docker/two_sources_USD_ETH_UniswapV2_coinbase_K_2_beta_1/figs/plot_ps.pdf`
  * For Figure 4(c), see `output_docker/three_sources_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1/figs/plot_ps.pdf`
  * For Figure 5(a), see `output_docker/one_source_USD_ETH_UniswapV2_K_1_beta_0/figs/plot_miscoverage.pdf`
  * For Figure 5(b), see `output_docker/two_sources_USD_ETH_UniswapV2_coinbase_K_2_beta_1/figs/plot_miscoverage.pdf`
  * For Figure 5(c), see `output_docker/three_sources_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1/figs/plot_miscoverage.pdf`
  * For Figure 6(a), see `output_docker/one_source_USD_ETH_UniswapV2_K_1_beta_0_two_sources_USD_ETH_UniswapV2_coinbase_K_2_beta_1_three_sources_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1/figs/plot_size.pdf`
  * For Figure 9(a), see `output_docker/three_sources_OneSigma_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1/figs/plot_ps.pdf`
  * For Figure 9(b), see `output_docker/three_sources_OneSigma_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1/figs/plot_miscoverage.pdf`

* To reproduce Table 1, Figure 7, Figure 8, and Figure 6(b), execute `./docker_scripts/docker_plot_INV_ETH.sh` or execute `./docker_scripts/docker_plot_INV_ETH_precomp.sh` if you wish to use precomputed results for reproducing results.
   * For Table 1, see `stdout`
   * For Figure 7(a), see `output_docker/one_source_INV_ETH_SushiSwap_K_1_beta_0/figs/plot_ps.pdf`
   * For Figure 7(b), see `output_docker/two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1/figs/plot_ps.pdf`
   * For Figure 7(c), see `output_docker/three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1/figs/plot_ps.pdf`
   * For Figure 8(a), see `output_docker/one_source_INV_ETH_SushiSwap_K_1_beta_0/figs/plot_miscoverage.pdf`
   * For Figure 8(b), see `output_docker/two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1/figs/plot_miscoverage.pdf`
   * For Figure 8(c), see `output_docker/three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1/figs/plot_miscoverage.pdf`
   * For Figure 6(b), see `output_docker/one_source_INV_ETH_SushiSwap_K_1_beta_0_two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1_three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1/figs/plot_size.pdf`


## Solidity Implementation

### Installation (5 human-minutes + 5 compute-minutes)

* Install [Docker](https://www.docker.com/)
* Pull a docker image via `docker pull ghcr.io/sslab-gatech/acon2-sol:latest`
* Clone this repository
* Execute `cd solidity`


### (Optional) Run Experiments (0 human-minutes + 30 compute-hours)

Reproducing results in our paper requires time. 
For a short running option which uses precomputed results in the docker image, you can skip this step. 

* Enter via `./docker_scripts/enter.sh`.
* Execute `./scripts/run.sh` for results in files, used for reproducing Table 2, Figure 10, and Figure 11. 
* Execute `./scripts/run_baseline.sh` for results in files, used for reproducing Table 2. 
* Exit from the docker image.

Note that the above execution consists of multiple random experiments, 
so running it under similar CPU overheads is recommanded for reproducing similar results as in the paper.  


### Validate Results (5 human-minutes + 5 compute-minutes)

* To reproduce Table 2, Figure 10, and Figure 11, execute `./docker_scripts/plot_sim.sh` or 
execute `./docker_scripts/plot_sim_precomp.sh` if you wish to use precomputed results for reproducing results.
  * For Table 2, see stdout
  * For Figure 10(a), see `output_docker/figs/acon2/plot-ps-K-3-alpha-0d01-iter-1.pdf`
  * For Figure 10(b), see `output_docker/figs/acon2/plot-error-var-K-3-alpha-0d01.pdf`
  * For Figure 11(a), see `output_docker/figs/acon2/plot-error-var-K-3-alphas.pdf`
  * For Figure 11(b), see `output_docker/figs/acon2/plot-error-var-K-4-alphas.pdf`
  * For Figure 11(c), see `output_docker/figs/acon2/plot-error-var-K-5-alphas.pdf`

