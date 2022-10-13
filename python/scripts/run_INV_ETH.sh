# three sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name three_sources_INV_ETH_SushiSwap_UniswapV2_coinbase \
	  --data.path data/price_INV_ETH/SushiSwap data/price_INV_ETH/UniswapV2 data/price_INV_ETH/coinbase \
	  --data.start_time 2022-03-31T00:00 \
	  --data.end_time 2022-05-31T23:59 \
	  --data.time_step_sec 10 \
	  --model_ps.name SpecialMVP SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
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
	  --model_ps.name SpecialMVP \
	  --model_ps.alpha 0.01 \
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
	  --model_ps.name SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.005 0.005 \
	  --model_ps.beta 1
"
