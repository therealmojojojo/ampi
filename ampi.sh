echo "Starting Ampi"
AMPI_HOME="/home/pi/Apps/ampi"
export PYTHONPATH=$PYTHONPATH:$AMPI_HOME/lib:$AMPI_HOME/components:$AMPI_HOME/resources:$AMPI_HOME/utils
echo $PYTHONPATH
python src/ampi.py -d $*
