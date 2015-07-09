import time
import sys
import threading

import mininet.link as link
from mininet.util import irange

from traffic import iperf, iperf_udp
from wireless import PhyModel
from mobility_model import RegionDistribution
from fill_rt import configure_downlink, configure_uplinks
from selection_algorithm import simple_tsa_algorithm, profiler_tsa_algorithm
from tsanet import TsaNet
# from graphics import represent_network
from argparse import ArgumentParser

# Command Line Arguments
parser = ArgumentParser(description="TSA Mininet Emulation")
parser.add_argument('--distance', '-d',
                    dest="distance",
                    type=int,
                    action="store",
                    help="distance between APs",
                    default=50)

parser.add_argument('--num-ues', '-n',
                    dest="num_ues",
                    type=int,
                    help="Number of wireless ue hosts",
                    default=16)

parser.add_argument('--algorithm', '-a',
                    dest="alg",
                    action="store",
                    help="Selection algorithm [rssi,simple_tsa,profiler_tsa]",
                    required=True)

parser.add_argument('--scenario', '-s',
                    dest="scenario",
                    type=int,
                    action="store",
                    help="simulation scenario [1 or 2]\n \tSCENARIO 1: \n"
                         "\t Each second, from UE(1) to UE(NUM_UEs), "
                         "a TCP full buffer tx to h1 is started until the end of simulation\n"
                         "\tSCENARIO 2: \n"
                         "\tFrom 0s to 16s, each second, from UE(1) to UE(16), a new UDP 100kbps tx "
                         "to h2 is started until the end of simulation\n"
                         "\tafter 16s, each second, from UE(17) to UE(16+NUM_UEs), "
                         "a TCP full buffer tx to h1 is started until the end of simulation",
                    required=True)

parser.add_argument('--run', '-r',
                    dest="run",
                    action="store",
                    help="run number",
                    default=1,
                    required=True)

args = parser.parse_args()

# Constant Definitions
UE_PHY_OPTS = {'Pt': 20, 'G_ant': 15, 'noise_fig': 7}
AP_PHY_OPTS = {'Pt': 46, 'G_ant': 25, 'noise_fig': 5, 'tdma': 'roundrobin'}
BW_SCALE = 50.0  # Link bandwidths are scaled down because tclink allowed maximum bandwidth is 1000Mbps.
SEED = args.run
DISTANCE = args.distance
NUM_UES = args.num_ues
SCENARIO = args.scenario
ALGORITHM = args.alg
AP_LIMIT = 4  # Each hosts select the AP from the AP_LIMIT APs with the higher RSSIs.

if SCENARIO == 1:
    print "SCENARIO 1: \n" \
          "\t Each second, from UE1 to UE{num_ues}, " \
          "a TCP full buffer tx to h1 is started until the end of simulation\n".format(num_ues=NUM_UES)

elif SCENARIO == 2:
    print "SCENARIO 2: \t\t\n" \
          "\tFrom 0s to 16s, each second, from UE1 to UE16, a new UDP 100kbps tx " \
          "to h2 is started until the end of simulation\n" \
          "\tafter 16s, each second, from UE17 to UE{num_ues}, " \
          "a TCP full buffer tx to h1 is started until the end of simulation\n".format(num_ues=16+NUM_UES)
else:
    print "Error UNKNOWN SCENARIO {scenario}".format(scenario=SCENARIO)
    sys.exit()

print "Be patient, Setting Up the Network..."

# MMWAVE PHY MODEL
mmWaveModel = PhyModel(PL0=75.85, alpha=3.73, W=1e9, kT=-174, pow_eff=0.5, bw_eff=0.8, max_se=4.8,
                       shad_std=8.36, seed=SEED, bw_scale_factor=BW_SCALE)

gridNet = TsaNet(autoStaticArp=True)

# Adding mmWaves Access Points in a grid
for index, pos in enumerate([(0, 0), (DISTANCE, 0), (0, DISTANCE), (DISTANCE, DISTANCE), (2 * DISTANCE, 0),
                             (3 * DISTANCE, 0), (2 * DISTANCE, DISTANCE), (3 * DISTANCE, DISTANCE),
                             (0, 2 * DISTANCE), (DISTANCE, 2 * DISTANCE), (0, 3 * DISTANCE), (DISTANCE, 3 * DISTANCE),
                             (2 * DISTANCE, 2 * DISTANCE), (3 * DISTANCE, 2 * DISTANCE),
                             (2 * DISTANCE, 3 * DISTANCE), (3 * DISTANCE, 3 * DISTANCE)]):
    gridNet.add_ap('sap%d' % (index + 1), pos, mmWaveModel, **AP_PHY_OPTS)
# Adding switches
for index, pos in enumerate(
        [(0.5 * DISTANCE, 0.5 * DISTANCE), (2.5 * DISTANCE, 0.5 * DISTANCE), (0.5 * DISTANCE, 2.5 * DISTANCE),
         (2.5 * DISTANCE, 2.5 * DISTANCE), (1.5 * DISTANCE, DISTANCE)]):
    gridNet.addSwitch('s10%d' % (index + 1))

# Defining Fixed hosts
gridNet.addHost('h1', ip='10.0.0.51')
gridNet.addHost('h2', ip='10.0.0.52')
# Defining Fixed Links
# from aps to aggregation switches
for i in irange(1, 16):
    gridNet.addLink('sap%d' % i, 's10%s' % ((i - 1) // 4 + 1), cls=link.TCLink, bw=10000 / BW_SCALE)
# from aggregation switches to core switch
for i in irange(1, 4):
    gridNet.addLink('s10%d' % i, 's105', cls=link.TCLink, bw=10000 / BW_SCALE)
# from fixed hosts to core switch
gridNet.addLink('h1', 's105', cls=link.TCLink, bw=40000 / BW_SCALE)
gridNet.addLink('h2', 's105', cls=link.TCLink, bw=40000 / BW_SCALE)
# Adding Wireless Tsa Hosts (UEs)
# Getting host position
# GRID definition: 3x3, 9 regions. probability of a node in each region is defined with a weight -> (row,column):weight.
# uniform_weights = {(1,1):1,(1,2):1,(1,3):1,(2,1):1,(2,2):1,(2,3):1,(3,1):1,(3,2):1,(3,3):1}
# We randomly distributed the UEs in the central region (2,2)-> 1. the other regions are empty -> (x,y):0
region_weights = {(1, 1): 0, (1, 2): 0, (1, 3): 0, (2, 1): 0, (2, 2): 1, (2, 3): 0,
                  (3, 1): 0, (3, 2): 0, (3, 3): 0}
region_gen = RegionDistribution(region_weights=region_weights, seed=SEED)
total_ues = NUM_UES if SCENARIO == 1 else NUM_UES + 15
for i in irange(1, total_ues):
    pos = region_gen.get_position(region_length=DISTANCE)
    tsa_host = gridNet.add_tsa_host('ue%02d' % i, pos, mmWaveModel, **UE_PHY_OPTS)
    tsa_host.init_wireless_links(ap_limit=AP_LIMIT)

# represent_network(gridNet)

# Start to auto-assign IPs
gridNet.start()

# Initial fill of routing tables with OpenFlow Rules
configure_uplinks(gridNet)
for tsa_host in gridNet.tsa_hosts:
    # Initial Ap selection
    tsa_host.select_ap(tsa_host.default_ap)
    configure_downlink(gridNet, tsa_host)
    print tsa_host

# For each AP estimate UE's wireless link bandwidth.
for ap in gridNet.tsa_aps:
    ap.tdma()

current_time = 0
total_time = total_ues

tcp_dst = gridNet['h1']
output = "output/TEST{scenario}-{d}m-{n}h-{alg}-r{run}-iperfTCP.log".format(d=DISTANCE, n=NUM_UES, alg=ALGORITHM,
                                                                        scenario=SCENARIO, run=SEED)
tcp_dst.cmd('iperf -s -i 1 -y c &>{out} &'.format(out=output))

udp_dst = gridNet['h2']
output = "output/TEST{scenario}-{d}m-{n}h-{alg}-r{run}-iperfUDP.log".format(d=DISTANCE, n=NUM_UES, alg=ALGORITHM,
                                                                      scenario=SCENARIO, run=SEED)
udp_dst.cmd('iperf -s -u -i 1 -y c &>{out} &'.format(out=output))

streams = []
index = 0
for src in gridNet.tsa_hosts:
    duration = total_time - current_time
    if index < 16 and SCENARIO == 2:
        # UDP Transmission
        src.required_tx_bw = 100000 / BW_SCALE  # 100Kbps
        tx_stream = threading.Thread(target=iperf_udp, name=None, args=(src, udp_dst, src.required_tx_bw, duration))
    else:
        # TCP Full Buffer Transmission
        src.required_tx_bw = 50000000000 / BW_SCALE  # Max 50Gbps for TCP full buffer traffic
        tx_stream = threading.Thread(target=iperf, name=None, args=(src, tcp_dst, duration))
    if ALGORITHM == 'rssi':
        src.select_ap(src.default_ap)
    elif ALGORITHM == 'simple_tsa':
        selected_ap = simple_tsa_algorithm(src.net, src)
        src.select_ap(selected_ap)
    elif ALGORITHM == 'profiler_tsa':
        selected_ap = profiler_tsa_algorithm(src.net, src)
        src.select_ap(selected_ap)
    else:
        print "error, unknown algorithm"
        sys.exit()
    src.selected_ap.active_tx_ues.append(src)
    src.selected_ap.tdma()
    tx_stream.start()
    streams.append(tx_stream)
    time.sleep(1)
    current_time += 1
    index += 1

for stream in streams:
    stream.join()

print("Be patient, we need to remove all virtual hosts and links, It could take several seconds...\n\n")
gridNet.stop()
