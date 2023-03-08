#!/bin/bash

K=$1
ALPHA=$2
EXPNAME=$3
AMMNAMES=""

ln -sf src_acon2 src
forge build --force --extra-output-files abi

for ((i=1; i<=$K; i++));
do
    AMMNAME="AMM${i}"
    AMMNAMES="$AMMNAMES $AMMNAME"
    
    # deploy factory
    forge create \
	  src/AMM/UniswapV2/v2-core/contracts/UniswapV2Factory.sol:UniswapV2Factory \
	  --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
	  --constructor-args 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 \
	  --extra-output-files abi \
	  --json > output/amm${i}_factory.json
    echo "- ${AMMNAME} factory is deployed."
    FACTORYADDR=$( cat output/amm${i}_factory.json | jq -r ".deployedTo" )

    # get init code hash
    cast call $FACTORYADDR "INIT_CODE_HASH()" > output/amm${i}_init_code_hash
    INITCODEHASH=$( cat output/amm${i}_init_code_hash )
    python3 script/add_init_code_hash.py --hash $INITCODEHASH

    # deploy router02
    forge create \
	  src/AMM/UniswapV2/periphery/contracts/UniswapV2Router02.sol:UniswapV2Router02 \
	  --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
	  --constructor-args ${FACTORYADDR} 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 \
	  --extra-output-files abi \
	  --json > output/amm${i}_router.json
    echo "- ${AMMNAME} router is deployed."

    # run LPs
    python3 script/lp.py --exp_name "$EXPNAME/lp" --address 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 --private_key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 --market_name $AMMNAME
    echo "- ${AMMNAME} liquidity is added."
done

# deploy ACon2
forge create \
      src/AMM/ACon2/ACon2.sol:ACon2 \
      --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
      --extra-output-files abi \
      --json > output/acon2.json
echo "- ACon2 is deployed."

# init ACon2
echo $AMMNAMES

python3 script/init_acon2.py --exp_name "$EXPNAME/init_acon2" --market_names $AMMNAMES --alpha $ALPHA
echo "- ACon2 is initialized."

