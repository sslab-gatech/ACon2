# three sources
python3.7 main.py \
	  --exp_name three_sources_zero_zero_zero \
	  --data.name ZeroPriceDataset \
	  --data.path data/zero data/zero data/zero \
	  --model_ps.beta 1

# two sources
python3.7 main.py \
	  --exp_name two_sources_zero_zero \
	  --data.name ZeroPriceDataset \
	  --data.path data/zero data/zero \
	  --model_ps.beta 0

# one sources
python3.7 main.py \
	  --exp_name one_sources_zero \
	  --data.name ZeroPriceDataset \
	  --data.path data/zero \
	  --model_ps.beta 0

