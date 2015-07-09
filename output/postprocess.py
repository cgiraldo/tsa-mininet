import glob
import datetime
from sys import argv


def process_file(name):
    with open(name) as inf:
        bitrate = dict()
        init_time = None
        for line in inf:
            values = line.split(',')
            current_time = datetime.datetime.strptime(values[0], '%Y%m%d%H%M%S')
            if init_time is None:
                init_time = current_time
            current_time = (current_time - init_time).total_seconds()
            host_seconds = values[6].split('-')
            # discarding summary entries in iperf
            if float(host_seconds[1]) - float(host_seconds[0]) == 1:
                # We multiply the goodput by the bandwidth scale factor of the simulation BW_SCALE=50.0
                current_bitrate = 50.0*float(values[8])
                bitrate[current_time] = bitrate.setdefault(current_time, 0) + current_bitrate
        output = name.replace('log', 'data')
        with open(output, 'w') as the_file:
            for key, value in bitrate.iteritems():
                the_file.write('{time} {bitrate}\n'.format(time=key, bitrate=value))


if len(argv) == 2:
    print argv[1]
    process_file(argv[1])
elif len(argv) == 1:
    for filename in glob.glob("*.log"):
        process_file(filename)

# for file in glob.glob("*iperfTCP.log"):
# parameters = re.match(r'(\d+)m-(\d+)h-(\w+)([-True]*)-limit(\d+)-iperfTCP.log',file)

