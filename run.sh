#!/bin/bash

# Exit on any failure
#set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python
	mn -c
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`


for run in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
for distance in 25 50 100; do
for algorithm in rssi simple_tsa; do
	python main_tsa.py --distance=$distance \
            --algorithm=$algorithm \
            --scenario=1 \
            --run=$run
done
done
done

for run in 1 2 3 4 5 6 7 8 9 10 11 12 14 15 16 17 18 19 20; do
for algorithm in rssi simple_tsa profiler_tsa; do
	python main_tsa.py \
            --algorithm=$algorithm \
            --scenario=2 \
            --run=$run
done
done

echo "Started at" $start
echo "Ended at" `date`
