#!/bin/bash
mkdir output

K=$1
EXPNAME=$2
AMMNAMES=""

##----------- trader
for ((i=1; i<=$K; i++));
do
    AMMNAME="AMM${i}"
    AMMNAMES="$AMMNAMES $AMMNAME"
    
    # deploy factory
    forge create \
	  src/AMM/UniswapV2Original/v2-core/contracts/UniswapV2Factory.sol:UniswapV2Factory \
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
	  src/AMM/UniswapV2Original/periphery/contracts/UniswapV2Router02.sol:UniswapV2Router02 \
	  --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
	  --constructor-args ${FACTORYADDR} 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 \
	  --extra-output-files abi \
	  --json > output/amm${i}_router.json
    echo "- ${AMMNAME} router is deployed."

    # run LPs
    python3 script/lp.py --exp_name "$EXPNAME/lp" --address 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 --private_key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 --market_name $AMMNAME
    echo "- ${AMMNAME} liquidity is added."
done


##----------- trader
screen -S trader -dm bash -c "python3 script/trader.py --exp_name ${EXPNAME}/trader1 --address 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266 --private_key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 --market_name $AMMNAMES"

# this is for collecting gas usage for the trader, so we don't run any arbitrageur and adversary.