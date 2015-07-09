set terminal pdf

#set title "total Goodput with mice and elephant traffic"

#set style line 99 linetype 1 linecolor rgb "#999999" lw 2
set key left top
#set key box linestyle 99
#set key spacing 1.2
#set nokey
set xrange [15:32]
#set yrange [0:70]
#set format y "%.0f"

#set size 2
#set size ratio 0.4

set ylabel "Total TCP Goodput (Gbps)"
set xlabel "time (seconds)"

#set style fill pattern 9 border
set style line 1 lc rgb 'red' lt 1 lw 3
set style line 2 lc rgb 'green' lt 2 lw 3
set style line 3 lc rgb 'blue' lt 3 lw 3

set output "test2.pdf"
# We convert the goodput from bps to Gbps
# The time is shifted 16s to be consisted with the simulation time
plot \
  "TEST2-50m-16h-profiler_tsa-conf.data" using ($1+16):(1e-9*$2) title "profiler+tsa" with linespoints ls 3,\
  "TEST2-50m-16h-profiler_tsa-conf.data" using ($1+16):(1e-9*$2):(1e-9*$3) notitle with errorbars ls 3,\
  "TEST2-50m-16h-simple_tsa-conf.data" using ($1+16):(1e-9*$2) title "tsa" with linespoints ls 1,\
  "TEST2-50m-16h-simple_tsa-conf.data" using ($1+16):(1e-9*$2):(1e-9*$3) notitle with errorbars ls 1,\
  "TEST2-50m-16h-rssi-conf.data" using ($1+16):(1e-9*$2) title "rssi" with linespoints ls 2,\
  "TEST2-50m-16h-rssi-conf.data" using ($1+16):(1e-9*$2):(1e-9*$3) notitle with errorbars ls 2
