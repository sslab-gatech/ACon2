for i in 1 2 3
do
    # deploy factory
    forge create \
	  src/AMM/UniswapV2/v2-core/contracts/UniswapV2Factory.sol:UniswapV2Factory \
	  --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
	  --constructor-args 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 \
	  --extra-output-files abi \
	  --json > output/amm${i}_factory.json
    echo "- AMM${i} factory is deployed."
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
    echo "- AMM${i} router is deployed."

    # run LPs
    python3 script/lp.py --exp_name test_lp --address 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 --private_key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 --market_name AMM${i}
    echo "- AMM${i} liquidity is added."
done

# deploy ACC
forge create \
      src/AMM/ACC/ACC.sol:ACC \
      --private-key 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6 \
      --extra-output-files abi \
      --json > output/acc.json
echo "- ACC is deployed."

# init ACC
python3 script/init_acc.py --exp_name init_acc --market_names AMM1 AMM2 AMM3 --beta 1
echo "- ACC is initialized."

