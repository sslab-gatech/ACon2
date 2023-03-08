OUTPUTDIR=${PWD}/output_docker
IMGTAG=ghcr.io/sslab-gatech/acon2-sol:latest
mkdir -p $OUTPUTDIR
echo "output directory: $OUTPUTDIR"
DOCKERCMD="docker run -v ${OUTPUTDIR}:/app/output --rm $IMGTAG"
ALGOUTPUTDIR=output_CR

$DOCKERCMD bash ./script/plot.sh $ALGOUTPUTDIR
