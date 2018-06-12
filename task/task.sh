#!/bin/bash
# This is a sample task.sh script invoked by the scheduler
# This script should be part of the user module, that invokes other python code, or 
# change const.py with python code directly(this script is not mandatory)

# purpose of the script is to:
# 1. prepare the data
# 2. invoke core module for training
# 3. copy trianing output back to storage

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Current directory is $DIR"

# split out the job detail, in this example
# 0000000000 as event id and test for the data path
EVENT_ID=$1
INPUT_PATH=$2

echo "Executing on event $EVENT_ID for $INPUT_PATH"

############ Prepare Data ###############
#########################################
DATA_PATH="${DIR}/input/${INPUT_PATH}"
mkdir -p ${DATA_PATH}
gsutil cp gs://trackml/${INPUT_PATH}/event${EVENT_ID}-*.csv $DATA_PATH
#cp ../input/${INPUT_PATH}/event${EVENT_ID}-*.csv $DATA_PATH

######## Call some other scripts #########
##########################################

#python db

##########################################

########### Copy training output #########
##########################################
gsutil cp ${DIR}/submission*.csv gs://trackml/submission


