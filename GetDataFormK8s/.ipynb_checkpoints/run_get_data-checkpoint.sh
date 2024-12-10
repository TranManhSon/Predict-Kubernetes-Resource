#!/bin/bash

PYTHON_SCRIPT="/root/KLTN/GetDataFormK8s/get_service_metric.py"

LOG_FILE="python_script.log"

nohup python3 $PYTHON_SCRIPT >> $LOG_FILE 2>&1 &

echo "Python script is running in the background with PID: $!"

