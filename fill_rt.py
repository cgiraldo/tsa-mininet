from subprocess import call

from mininet.util import irange


def configure_downlink(net, tsa_host):
    ue_ip = tsa_host.host.IP()
    call(["ovs-ofctl", 'add-flow', tsa_host.tsa_switch.name,
          "idle_timeout=0,priority=33001,"
          "dl_type=0x800,nw_dst={ip},actions=output:{port}".format(ip=ue_ip, port=tsa_host.in_port)])
    ap_name = tsa_host.selected_ap.name
    ap = net[ap_name]
    # add ap OF-rule for downlink in ap
    for ap_intf, tsa_switch_intf in ap.connectionsTo(tsa_host.tsa_switch):
        call(['ovs-ofctl', 'add-flow', ap_name, 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                'actions=output:{out}'.format(ip=ue_ip, out=ap.ports[ap_intf])])

    for switch_name in ['s101', 's102', 's103', 's104']:
        switch = net[switch_name]
        for ap_intf, switch_intf in ap.connectionsTo(switch):
            # downlink rule
            call(['ovs-ofctl', 'add-flow', switch_name, 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                        'actions=output:{out}'.format(ip=ue_ip,
                                                                                      out=switch.ports[switch_intf])])
            for switch_intf2, s105_intf in switch.connectionsTo(net['s105']):
                call(['ovs-ofctl', 'add-flow', 's105', 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                       'actions=output:{out}'.format(ip=ue_ip,
                                                                                     out=net['s105'].ports[s105_intf])])


def configure_uplinks(net):
    for host_name in ['h1', 'h2']:
        host = net[host_name]
        switch = net['s105']
        for s105_intf, host_intf in switch.connectionsTo(host):
            call(['ovs-ofctl', 'add-flow', 's105', 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                   'actions=output:{out}'.format(ip=host.IP(),
                                                                                 out=switch.ports[s105_intf])])
        for switch_name in ['s101', 's102', 's103', 's104']:
            switch = net[switch_name]
            for switch_intf, s105_intf in switch.connectionsTo(net['s105']):
                call(['ovs-ofctl', 'add-flow', switch_name, 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                            'actions=output:{out}'.format(ip=host.IP(),
                                                                                          out=switch.ports[
                                                                                              switch_intf])])
        for i in irange(1, 16):
            ap_name = "sap%d" % i
            switch_name = "s10%d" % ((i - 1) / 4 + 1)
            ap = net[ap_name]
            switch = net[switch_name]
            for ap_intf, switch_intf in ap.connectionsTo(switch):
                call(['ovs-ofctl', 'add-flow', ap_name, 'idle_timeout=0,priority=33000,dl_type=0x800,nw_dst={ip},'
                                                        'actions=output:{out}'.format(ip=host.IP(),
                                                                                      out=ap.ports[ap_intf])])
