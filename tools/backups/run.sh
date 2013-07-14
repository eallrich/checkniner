#!/bin/bash

STARTING_DIR=$(cd "$(dirname "$0")" && pwd)
echo "Starting in $STARTING_DIR"

ACTIVATOR=$(readlink -f "$STARTING_DIR/../../bin/activate")
echo "Trying to activate virtualenv at $ACTIVATOR"
source $ACTIVATOR

cd $STARTING_DIR
python collect.py
