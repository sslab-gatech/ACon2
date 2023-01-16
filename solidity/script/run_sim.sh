mkdir output
./script/deploy.sh $1
./script/run_traders.sh
./script/run_adv.sh
./script/run_arb.sh
