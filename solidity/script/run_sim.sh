#!/bin/bash
mkdir output
./script/deploy.sh $1 $2 $3
./script/run_traders.sh $1 $3
./script/run_adv.sh $1 $3
./script/run_arb.sh $1 $3
