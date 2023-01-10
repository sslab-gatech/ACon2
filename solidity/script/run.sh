ALPHA=0d01
DURATION=1800
for i in {1..10}
do
    echo "run miners"
    screen -S miners -dm bash -c "./script/run_node.sh"
    sleep 10
    echo "run a sim"
    ./script/run_sim.sh
    echo "run a reader"
    screen -S reader -dm bash -c "python3 script/read_acc.py --exp_name acon2_${ALPHA}_iter_${i}"
    echo "wait ${DURATION} sec..."
    sleep $DURATION
    screen -X -S miners quit
    screen -X -S adv quit
done


