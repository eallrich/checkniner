#!/bin/bash

cd $(dirname $0)
LOGFILE="clean.log"
echo "`date +%Y-%m-%dT%H:%M:%S` | $0 invoked. Deleting:" >> $LOGFILE
LATEST="latest.tar.gz"
TARGET=$(basename `readlink -f $LATEST`)
ls | grep .tar.gz | grep --invert-match -e $LATEST -e $TARGET | tee --append $LOGFILE | xargs rm
