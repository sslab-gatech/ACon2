DURATION=1800

for K in 3 5 1
do
    for ALPHA in 0.01 0.001
    do
	for i in {1..5}
	do
	    echo "========== K = ${K}, alpha = ${ALPHA}, iter = ${i} =========="

	    echo "run miners"
	    screen -S miners -dm bash -c "./script/run_node.sh"
	    sleep 5

	    echo "run a sim"
	    ./script/run_sim.sh $K $ALPHA

	    echo "run a reader"
	    AMMNAMES=""
	    for ((j=1; j<=$K; j++));
	    do
		AMMNAMES="$AMMNAMES AMM${j}"
	    done
	    screen -S reader -dm bash -c "python3 script/read_acc.py --exp_name acon2_K_${K}_alpha_${ALPHA//./d}_iter_${i}_duration_${DURATION} --market_names ${AMMNAMES}"
	    
	    echo "wait ${DURATION} sec..."
	    sleep $DURATION
	    screen -X -S miners quit
	    screen -X -S adv quit
	    rm /tmp/.tmp* -rf
	done
    done
done

