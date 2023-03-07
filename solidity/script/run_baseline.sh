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

echo "wait ${DURATION} sec..."
sleep $DURATION # wait until traders make 500 transactions
screen -X -S miners quit
screen -X -S adv quit
rm -rf /tmp/.tmp*

