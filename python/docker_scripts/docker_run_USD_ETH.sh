OUTPUTDIR=${PWD}/output_docker
IMGTAG=ghcr.io/sslab-gatech/acon2:latest
mkdir -p $OUTPUTDIR
echo "output directory: $OUTPUTDIR"
DOCKERCMD="docker run -v ${OUTPUTDIR}:/app/output --rm $IMGTAG"
NOISE=4.6 # exp(4.6) \approx 100
NCP=0

# one sources
$DOCKERCMD python3 main.py \
	  --exp_name one_source_USD_ETH_UniswapV2 \
	  --data.path data/price_USD_ETH/UniswapV2 \
	  --model_base.name KF1D \
	  --model_base.state_noise_init $NOISE \
	  --model_base.obs_noise_init $NOISE \
	  --model_ps.name SpecialMVP \
	  --model_ps.alpha 0.01 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 0

# two sources
$DOCKERCMD python3 main.py \
	  --exp_name two_sources_USD_ETH_UniswapV2_coinbase \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase \
	  --model_base.name KF1D KF1D \
	  --model_base.state_noise_init $NOISE $NOISE \
	  --model_base.obs_noise_init $NOISE $NOISE \
	  --model_ps.name SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.005 0.005 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 1

# three sources
$DOCKERCMD python3 main.py \
	  --exp_name three_sources_USD_ETH_UniswapV2_coinbase_binance \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase data/price_USD_ETH/binance \
	  --model_base.name KF1D KF1D KF1D \
	  --model_base.state_noise_init $NOISE $NOISE $NOISE \
	  --model_base.obs_noise_init $NOISE $NOISE $NOISE \
	  --model_ps.name SpecialMVP SpecialMVP SpecialMVP \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 1

# baseline: sigma-ACon2
$DOCKERCMD python3 main.py \
	  --exp_name three_sources_OneSigma_USD_ETH_UniswapV2_coinbase_binance \
	  --data.path data/price_USD_ETH/UniswapV2 data/price_USD_ETH/coinbase data/price_USD_ETH/binance \
	  --model_base.name KF1D KF1D KF1D \
	  --model_base.state_noise_init $NOISE $NOISE $NOISE \
	  --model_base.obs_noise_init $NOISE $NOISE $NOISE \
	  --model_ps.name OneSigma OneSigma OneSigma \
	  --model_ps.alpha 0.00333 0.00333 0.00333 \
	  --model_ps.nonconsensus_param	$NCP \
	  --model_ps.beta 1
