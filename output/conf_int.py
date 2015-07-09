import math
from sys import argv
import glob

def sample_variance(my_list):
    variance = 0
    mean = average(my_list)
    for i in my_list:
        variance += (mean - i) ** 2
    return variance / (len(my_list) - 1)


def average(my_list):
    return sum(my_list) / len(my_list)


def calculate_error(my_list):
    error = 2 * math.sqrt(sample_variance(my_list) / len(my_list))
    return average(my_list), error


def conf_interval(output_name):
    result_rounds = dict()
    final_result = dict()
    runs = glob.glob(output_name+'*iperfTCP.data')
    print "Getting Confidence Intervals for " + argv[1] + " using {num_runs} runs".format(num_runs=len(runs))
    for output_data in runs:
        with open(output_data) as input_file:
            for line in input_file:
                values = line.split(' ')
                current_time = float(values[0])
                current_bitrate = float(values[1])
                result_rounds.setdefault(current_time, []).append(current_bitrate)

    for key, value in result_rounds.iteritems():
        if len(value) > 1:
            result, error = calculate_error(value)
            final_result[key] = result, error

    with open(output_name + '-conf.data', 'w') as the_file:
        for key, value in sorted(final_result.iteritems()):
            the_file.write('{time} {bitrate} {error}\n'.format(time=key, bitrate=value[0], error=value[1]))

if len(argv) == 2:
    conf_interval(argv[1])
