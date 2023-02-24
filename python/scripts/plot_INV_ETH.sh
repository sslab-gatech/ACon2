#python3.7 plots/plot_ps.py --exp_name single_INV_ETH_SushiSwap --y_min 0 --y_max 7
#python3.7 plots/plot_ps.py --exp_name single_INV_ETH_UniswapV2 --y_min 0 --y_max 7
python3.7 plots/plot_ps.py --exp_name one_source_INV_ETH_SushiSwap_K_1_beta_0 --y_min 0 --y_max 30 --y_max_mc 0.05 --time_start 2022-04-01T00:00 
python3.7 plots/plot_ps.py --exp_name two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1 --y_min 0 --y_max 30 --y_max_mc 0.05 --time_start 2022-04-01T00:00
python3.7 plots/plot_ps.py --exp_name three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1 --y_min 0 --y_max 30 --y_max_mc 0.05 --time_start 2022-04-01T00:00

python3.7 plots/plot_size.py --exp_names one_source_INV_ETH_SushiSwap_K_1_beta_0 two_sources_INV_ETH_SushiSwap_UniswapV2_K_2_beta_1 three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase_K_3_beta_1 --log_scale


PYTHONPATH=. python3.7 plots/plot_highlight.py
