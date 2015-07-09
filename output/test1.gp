set terminal pdf

#set title "total TCP Goodput vs AP selection algorithm"

#set style line 99 linetype 1 linecolor rgb "#999999" lw 2
set key left top
#set key box linestyle 99
#set key spacing 1.2
#set nokey

set xrange [0:16]
#set yrange [0:70]
#set format y "%.0f"

#set size 2
#set size ratio 0.4

set ylabel "Total TCP Goodput (Gbps)"
set xlabel "time (seconds)"

#set style fill pattern 9 border 
set style line 1 lc rgb 'red' lt 1 lw 3
set style line 2 lc rgb 'red' lt 2 lw 3
set style line 3 lc rgb 'blue' lt 3 lw 2
set style line 4 lc rgb 'blue' lt 4 lw 2
set style line 5 lc rgb 'green' lt 5 lw 1
set style line 6 lc rgb 'green' lt 6 lw 1


set output "test1.pdf"
# We convert the goodput from bps to Gbps
plot \
  "TEST1-25m-16h-simple_tsa-conf.data" using 1:(1e-9*$2) title "tsa(d=25)" with linespoints ls 1,\
  "TEST1-25m-16h-simple_tsa-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 1,\
  "TEST1-25m-16h-rssi-conf.data" using 1:(1e-9*$2) title "rssi(d=25)" with linespoints ls 2,\
  "TEST1-25m-16h-rssi-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 2,\
  "TEST1-50m-16h-simple_tsa-conf.data" using 1:(1e-9*$2) title "tsa(d=50)" with linespoints ls 3,\
  "TEST1-50m-16h-simple_tsa-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 3,\
  "TEST1-50m-16h-rssi-conf.data" using 1:(1e-9*$2) title "rssi(d=50)" with linespoints ls 4,\
  "TEST1-50m-16h-rssi-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 4,\
  "TEST1-100m-16h-simple_tsa-conf.data" using 1:(1e-9*$2) title "tsa(d=100)" with linespoints ls 5,\
  "TEST1-100m-16h-simple_tsa-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 5,\
  "TEST1-100m-16h-rssi-conf.data" using 1:(1e-9*$2) title "rssi(d=100)" with linespoints ls 6,\
  "TEST1-100m-16h-rssi-conf.data" using 1:(1e-9*$2):(1e-9*$3) notitle with errorbars ls 6
