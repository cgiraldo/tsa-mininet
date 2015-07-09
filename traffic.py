from tsanet import TsaHost


def iperf(src, dst, duration=10):
    output = 'output/iperfclientTCP-{src}-{dst}.txt'.format(src=src.name, dst=dst.name)
    cmd = 'iperf -c {ip} -t {duration}'.format(
        ip=dst.IP(), duration=duration, output=output)
    print "host {src} cmd {cmd}".format(src=src.name, cmd=cmd)
    if isinstance(src, TsaHost):
        src.host.cmd(cmd)
        # deactivate tx user
        print "DEACTIVATING TX TCP UE"
        src.required_tx_bw = 0
        src.selected_ap.active_tx_ues.remove(src)
    else:
        src.cmd(cmd)


def iperf_udp(src, dst, bitrate, duration=10):
    output = 'output/iperfclientUDP-{src}-{dst}.txt'.format(src=src.name, dst=dst.name)
    # size of udp packets 64 bytes
    cmd = 'iperf -c {ip} -u -b{bitrate} -l64 -t {duration}'.format(
        ip=dst.IP(), bitrate=bitrate, duration=duration, output=output)
    print "host {src} cmd {cmd}".format(src=src.name, cmd=cmd)
    if isinstance(src, TsaHost):
        src.host.cmd(cmd)
        # deactivate tx user
        src.required_tx_bw = 0
        src.selected_ap.active_tx_ues.remove(src)
    else:
        src.cmd(cmd)


def itg(src, dst, bitrate, duration=10):
    packets_s = int(bitrate * 1000000 / 4096)
    cmd = 'ITGSend -C {packets} -c 512 -a {ip} -t {duration}'.format(
        packets=packets_s, ip=dst.IP(), duration=duration * 1000)
    if isinstance(src, TsaHost):
        src.host.cmd(cmd)
        # deactivate tx user
        src.required_tx_bw = 0
        src.selected_ap.active_tx_ues.remove(src)
    else:
        src.cmd(cmd)
