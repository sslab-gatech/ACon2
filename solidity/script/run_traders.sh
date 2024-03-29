#!/bin/bash
K=$1
EXPNAME=$2
AMMNAMES=""
for ((j=1; j<=$K; j++));
do
    AMMNAMES="$AMMNAMES AMM${j}"
done

screen -S trader -dm bash -c "python3 script/trader.py --exp_name ${EXPNAME}/trader1 --address 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266 --private_key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 --market_name $AMMNAMES"
# screen -dm bash -c "python3 script/trader.py --exp_name test_trader2 --address 0x70997970c51812dc3a010c7d01b50e0d17dc79c8 --private_key 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d --market_name AMM1 AMM2 AMM3"
# screen -dm bash -c "python3 script/trader.py --exp_name test_trader3 --address 0x3c44cdddb6a900fa2b585dd299e03d12fa4293bc --private_key 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a --market_name AMM1 AMM2 AMM3"
# screen -dm bash -c "python3 script/trader.py --exp_name test_trader4 --address 0x90f79bf6eb2c4f870365e785982e1f101e93b906 --private_key 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6 --market_name AMM1 AMM2 AMM3"


# (0) 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266 (10000 ETH)
# (1) 0x70997970c51812dc3a010c7d01b50e0d17dc79c8 (10000 ETH)
# (2) 0x3c44cdddb6a900fa2b585dd299e03d12fa4293bc (10000 ETH)
# (3) 0x90f79bf6eb2c4f870365e785982e1f101e93b906 (10000 ETH)
# (4) 0x15d34aaf54267db7d7c367839aaf71a00a2c6a65 (10000 ETH)
# (5) 0x9965507d1a55bcc2695c58ba16fb37d819b0a4dc (10000 ETH)
# (6) 0x976ea74026e726554db657fa54763abd0c3a0aa9 (10000 ETH)
# (7) 0x14dc79964da2c08b23698b3d3cc7ca32193d9955 (10000 ETH)
# (8) 0x23618e81e3f5cdf7f54c3d65f7fbc0abf5b21e8f (10000 ETH)
# (9) 0xa0ee7a142d267c1f36714e4a8f75612f20a79720 (10000 ETH)

# Private Keys
# ==================

# (0) 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
# (1) 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
# (2) 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a
# (3) 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6
# (4) 0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a
# (5) 0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba
# (6) 0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e
# (7) 0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356
# (8) 0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97
# (9) 0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6


