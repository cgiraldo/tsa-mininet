#!/bin/bash

echo "converting iperf log files to gnuplot data"
cd output
python postprocess.py
echo "calculating confidence intervals for TEST1"
python conf_int.py TEST1-100m-16h-simple_tsa
python conf_int.py TEST1-50m-16h-simple_tsa
python conf_int.py TEST1-25m-16h-simple_tsa
python conf_int.py TEST1-100m-16h-rssi
python conf_int.py TEST1-50m-16h-rssi
python conf_int.py TEST1-25m-16h-rssi
echo "calculating confidence intervals for TEST2"
python conf_int.py TEST2-50m-16h-rssi
python conf_int.py TEST2-50m-16h-simple_tsa
python conf_int.py TEST2-50m-16h-profiler_tsa
echo "generating graphs"
gnuplot test1.gp
gnuplot test2.gp
cd ..
echo "pdf graphs generated in output folder"