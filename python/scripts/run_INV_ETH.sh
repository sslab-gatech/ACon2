# as the data sequence is short, we don't have enough time to learn noise level before the price manipulation.
# So, we choose exp(0.1), assuming that the algorithm has knowledge on the noise level at the beginning of the data
# to have a right behavior of our algorithm under the price manipulation.

NOISE=0.1 # exp(0.1) \approx 1, which makes a consensus set size around 0.5 on initial data
# NOISE=4.6 # exp(4.6) \approx 100
NCP=0.2735 # max(prices) - min(prices) at time t=1

# three sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase \
	  --data.path data/price_INV_ETH/SushiSwap data/price_INV_ETH/UniswapV2 data/price_INV_ETH/coinbase \
	  --data.start_time 2022-03-31T00:00 \
	  --data.end_time 2022-05-31T23:59 \
	  --data.time_step_sec 10 \
	  --model_base.name KF1D KF1D KF1D \
	  --model_base.state_noise_init $NOISE $NOISE $NOISE \
	  --model_base.obs_noise_init $NOISE $NOISE $NOISE \
	  --model_ps.name SpecialMVP SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 1
"

# one source
screen -dm bash -c "
python3.7 main.py \
	  --exp_name one_source_INV_ETH_SushiSwap \
	  --data.path data/price_INV_ETH/SushiSwap \
	  --data.start_time 2022-03-31T00:00 \
	  --data.end_time 2022-05-31T23:59 \
	  --data.time_step_sec 10 \
	  --model_base.name KF1D \
	  --model_base.state_noise_init $NOISE \
	  --model_base.obs_noise_init $NOISE \
	  --model_ps.name SpecialMVP \
	  --model_ps.alpha 0.01 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 0
"

# two sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name two_sources_INV_ETH_SushiSwap_UniswapV2 \
	  --data.path data/price_INV_ETH/SushiSwap data/price_INV_ETH/UniswapV2 \
	  --data.start_time 2022-03-31T00:00 \
	  --data.end_time 2022-05-31T23:59 \
	  --data.time_step_sec 10 \
	  --model_base.name KF1D KF1D \
	  --model_base.state_noise_init $NOISE $NOISE \
	  --model_base.obs_noise_init $NOISE $NOISE \
	  --model_ps.name SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.005 0.005 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 1
"
