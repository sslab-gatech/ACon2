K=$1
EXPNAME=$2
AMMNAMES=""
for ((j=1; j<=$K; j++));
do
    AMMNAMES="$AMMNAMES AMM${j}"
done

screen -S arb1 -dm bash -c "python3 script/arb.py --exp_name ${EXPNAME}/arb1 --address 0x9965507d1a55bcc2695c58ba16fb37d819b0a4dc --private_key 0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba --markets $AMMNAMES"
# screen -S arb2 -dm bash -c "python3 script/arb.py --exp_name ${EXPNAME}/arb2 --address 0x976ea74026e726554db657fa54763abd0c3a0aa9 --private_key 0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e --markets $AMMNAMES"
# screen -S arb3 -dm bash -c "python3 script/arb.py --exp_name ${EXPNAME}/arb3 --address 0x14dc79964da2c08b23698b3d3cc7ca32193d9955 --private_key 0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356 --markets $AMMNAMES"
