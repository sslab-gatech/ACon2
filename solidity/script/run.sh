DURATION=3600

for ALPHA in 0.01 0.001
do
    for i in {1..10}
    do
	echo "========== alpha = ${ALPHA}, iter = ${i} =========="
	echo "run miners"
	screen -S miners -dm bash -c "./script/run_node.sh"
	sleep 10
	echo "run a sim"
	./script/run_sim.sh $ALPHA
	echo "run a reader"
	screen -S reader -dm bash -c "python3 script/read_acc.py --exp_name acon2_basealpha_${ALPHA//./d}_iter_${i}_duration_${DURATION}"
	echo "wait ${DURATION} sec..."
	sleep $DURATION
	screen -X -S miners quit
	screen -X -S adv quit
	rm /tmp/.tmp* -rf
    done
done


