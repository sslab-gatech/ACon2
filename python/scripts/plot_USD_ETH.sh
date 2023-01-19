#python3.7 plots/plot_ps.py --exp_name single_INV_ETH_SushiSwap --y_min 0 --y_max 7
#python3.7 plots/plot_ps.py --exp_name single_INV_ETH_UniswapV2 --y_min 0 --y_max 7
python3.7 plots/plot_ps.py --exp_name one_source_USD_ETH_UniswapV2_K_1_beta_0 --y_max_mc 0.1 --step 500
python3.7 plots/plot_ps.py --exp_name two_sources_USD_ETH_UniswapV2_coinbase_K_2_beta_1 --y_max_mc 0.1 --step 500
python3.7 plots/plot_ps.py --exp_name three_sources_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1 --y_max_mc 0.1 --step 500
python3.7 plots/plot_size.py --exp_names one_source_USD_ETH_UniswapV2_K_1_beta_0 two_sources_USD_ETH_UniswapV2_coinbase_K_2_beta_1 three_sources_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1 --log_scale


python3.7 plots/plot_ps.py --exp_name three_sources_OneSigma_USD_ETH_UniswapV2_coinbase_binance_K_3_beta_1 --y_max_mc 0.6 --step 500 --ours_name '$\sigma$-ACon$^2$'

