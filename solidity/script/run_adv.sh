K=$1
EXPNAME=$2
AMMNAMES=""
for ((j=1; j<=$K; j++));
do
    AMMNAMES="$AMMNAMES AMM${j}"
done

screen -S adv -dm bash -c "python3 script/adv.py --exp_name ${EXPNAME}/adv --address 0x23618e81e3f5cdf7f54c3d65f7fbc0abf5b21e8f --private_key 0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97 --market_names $AMMNAMES"
