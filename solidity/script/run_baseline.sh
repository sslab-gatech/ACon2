#!/bin/bash

DURATION=300
K=3
EXPNAME=baseline

echo "run miners"
screen -S miners -dm bash -c "./script/run_node.sh"
sleep 5

echo "depoly AMMs and run traders"
screen -S sim -dm bash -c "./script/run_sim_baseline.sh $K $EXPNAME"
while screen -list | grep -q sim
do
    sleep 1
done


##----------- trader
AMMNAMES=""
for ((i=1; i<=$K; i++));
do
    AMMNAME="AMM${i}"
    AMMNAMES="$AMMNAMES $AMMNAME"
done
screen -S trader -dm bash -c "python3 script/trader.py --exp_name ${EXPNAME}/trader1 --address 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266 --private_key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 --market_name $AMMNAMES"

# this is for collecting gas usage for the trader, so we don't run any arbitrageur and adversary.



echo "wait ${DURATION} sec..."
sleep $DURATION # wait until traders make 500 transactions
screen -X -S miners quit
screen -X -S adv quit
rm -rf /tmp/.tmp*

