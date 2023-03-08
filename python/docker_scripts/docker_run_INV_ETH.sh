OUTPUTDIR=${PWD}/output_docker
IMGTAG=ghcr.io/sslab-gatech/acon2:latest
mkdir -p $OUTPUTDIR
echo "output directory: $OUTPUTDIR"
DOCKERCMD="docker run -v ${OUTPUTDIR}:/app/output --rm $IMGTAG"
NOISE=0.1 # exp(0.1) \approx 1, which makes a consensus set size around 0.5 on initial data
NCP=0.2735 # max(prices) - min(prices) at time t=1

# one source
$DOCKERCMD python3 main.py \
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

# two sources
$DOCKERCMD python3 main.py \
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

# three sources
$DOCKERCMD python3 main.py \
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

