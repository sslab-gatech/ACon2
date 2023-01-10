# one sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name one_source_USD_ETH_UniswapV2 \
	  --data.path data/price_USD_ETH/UniswapV2 \
	  --model_ps.name SpecialMVP \
	  --model_ps.alpha 0.01 \
	  --model_ps.beta 0
"

# two sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name two_sources_USD_ETH_UniswapV2_coinbase \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase \
	  --model_ps.name SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.005 0.005 \
	  --model_ps.beta 1
"

# three sources
screen -dm bash -c "
python3.7 main.py \
	  --exp_name three_sources_USD_ETH_UniswapV2_coinbase_binance \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase data/price_USD_ETH/binance \
	  --model_ps.name SpecialMVP SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
	  --model_ps.beta 1
"

# baseline
screen -dm bash -c "
python3.7 main.py \
	  --exp_name three_sources_OneSigma_USD_ETH_UniswapV2_coinbase_binance \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase data/price_USD_ETH/binance \
	  --model_ps.name OneSigma OneSigma OneSigma \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
	  --model_ps.beta 1
"
