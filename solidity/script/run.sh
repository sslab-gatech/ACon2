DURATION=3600

for K in 3 4 5
do
    AMMNAMES=""
    for ((j=1; j<=$K; j++));
    do
	AMMNAMES="$AMMNAMES AMM${j}"
    done
    for ALPHA in 0.01 0.001
    do
	for i in {1..5}
	do
	    echo "========== K = ${K}, alpha = ${ALPHA}, iter = ${i} =========="
	    EXPNAME="acon2_K_${K}_alpha_${ALPHA//./d}_iter_${i}_duration_${DURATION}"
	    
	    echo "run miners"
	    screen -S miners -dm bash -c "./script/run_node.sh"
	    sleep 5

	    echo "run a sim"
	    ./script/run_sim.sh $K $ALPHA $EXPNAME

	    echo "run a reader"
	    screen -S reader -dm bash -c "python3 script/read_acc.py --exp_name $EXPNAME --market_names ${AMMNAMES}"
	    
	    echo "wait ${DURATION} sec..."
	    sleep $DURATION
	    screen -X -S miners quit
	    screen -X -S adv quit
	    rm /tmp/.tmp* -rf
	done
    done
done

