echo "Starting Ampi"
export PYTHONPATH=$PYTHONPATH:./lib:./components:./resources:./utils
echo $PYTHONPATH
python src/ampi.py -d $*
