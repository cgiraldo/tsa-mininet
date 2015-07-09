from subprocess import call

from mininet.net import Mininet
from mininet.link import TCLink

from wireless import WirelessHost


class TsaHost(WirelessHost):
    def __init__(self, net, name, *args, **kwargs):
        super(TsaHost, self).__init__(name, *args, **kwargs)
        self.net = net
        self.host = net.addHost(name, isUe=True)
        self.tsa_switch = net.addSwitch('s%s' % name, isTsa=True)
        self.link = net.addLink(self.host, self.tsa_switch)
        self.in_port = self.tsa_switch.ports[self.link.intf2]
        self.required_tx_bw = 0
        self.required_rx_bw = 0
        self.assigned_tx_bw = 0
        self.assigned_rx_bw = 0
        self.available_tx_bw = 0
        self.available_rx_bw = 0
        self.selected_ap = None
        self.default_ap = None
        self.aps_phy_params = []
        self.available_aps = dict()

    def init_wireless_links(self, ap_limit=4):
        phy_params = self.phy_model.get_phy_params(self)
        for phy_param in phy_params[0:ap_limit]:
            ap_switch = phy_param['ap'].switch
            self.net.addLink(self.tsa_switch, ap_switch, cls=TCLink)
            self.available_aps[phy_param['ap'].name] = phy_param
        # default selection is rssi
        self.aps_phy_params = phy_params[0:ap_limit]
        self.default_ap = phy_params[0]['ap']

    def select_ap(self, ap):
        # Configure uplink selection
        if self.selected_ap != ap:
            self.selected_ap = ap
            self.available_tx_bw = self.available_aps[ap.name]['ul_bitrate']
            self.available_rx_bw = self.available_aps[ap.name]['dl_bitrate']
            src_intf = self.tsa_switch.connectionsTo(ap.switch)[0][0]
            port = self.tsa_switch.ports[src_intf]
            call(["ovs-ofctl", 'add-flow', self.tsa_switch.name,
                  "idle_timeout=0,priority=33000,dl_type=0x800,nw_dst=10.0.0.51,actions=output:{port}".format(
                      port=port)])
            call(["ovs-ofctl", 'add-flow', self.tsa_switch.name,
                  "idle_timeout=0,priority=33000,dl_type=0x800,nw_dst=10.0.0.52,actions=output:{port}".format(
                      port=port)])

    def __repr__(self):
        return "name: {name} -> \tselected_ap: {sel_ap}\n" \
               "\tavailable_tx: {av_tx} \tavailable_rx: {av_rx}\n" \
               "\trequired_tx: {req_tx} \trequired_rx: {req_rx}\n" \
               "\tassigned_tx: {as_tx} \tassigned_rx: {as_rx}\n".format(name=self.name, sel_ap=self.selected_ap.name,
                                                                        av_tx=self.available_tx_bw,
                                                                        av_rx=self.available_rx_bw,
                                                                        as_tx=self.assigned_tx_bw,
                                                                        as_rx=self.assigned_rx_bw,
                                                                        req_tx=self.required_tx_bw,
                                                                        req_rx=self.required_rx_bw)


class TsaAp(WirelessHost):
    def __init__(self, net, name, *args, **kwargs):
        self.tdma_mode = kwargs.pop('tdma', 'roundrobin')
        super(TsaAp, self).__init__(name, *args, **kwargs)
        self.net = net
        self.switch = self.net.addSwitch(name, isAp=True)
        self.phy_model.register_ap(self)
        self.active_tx_ues = []
        self.active_rx_ues = []

    def tdma(self):
        if self.tdma_mode == 'static':
            # def tdma_static_slots(self):
            # this model a dumb scheduler assigning the same amount of time to each active user
            total_active_users = len(self.active_tx_ues) + len(self.active_rx_ues)
            for node in self.active_tx_ues:
                node.assigned_tx_bw = node.available_tx_bw / total_active_users
            for node in self.active_rx_ues:
                node.assigned_rx_bw = node.available_rx_bw / total_active_users
        elif self.tdma_mode == 'roundrobin' or self.tdma_mode == 'rr':
            # this models a round robin scheduler among active users
            total_slots = 1000
            for node in self.active_tx_ues:
                node.assigned_tx_bw = 0
            for node in self.active_rx_ues:
                node.assigned_rx_bw = 0
            # We assign 1000 time slots:
            available_slots = total_slots
            while available_slots > 0:
                prev_av_slots = available_slots
                for node in self.active_tx_ues:
                    if node.assigned_tx_bw < node.required_tx_bw:
                        node.assigned_tx_bw += node.available_tx_bw / total_slots
                        available_slots -= 1
                for node in self.active_rx_ues:
                    if node.assigned_rx_bw < node.required_rx_bw:
                        node.assigned_rx_bw += node.available_rx_bw / total_slots
                        available_slots -= 1
                if available_slots == prev_av_slots:
                    break
                    # Update Link bandwidths accordingly with the assigned_bws
                    # The connection is done with the host internal tsa_switch
        for node in self.active_tx_ues:
            src_intf = node.tsa_switch.connectionsTo(self.switch)[0][0]
            bw = node.assigned_tx_bw / 1000000.0
            src_intf.config(bw=bw)
            print "{tx}->{ap} uplink bandwidth = {bw}Mbps".format(tx=node.name, ap=self.name, bw=bw)
        for node in self.active_rx_ues:
            dst_intf = node.tsa_switch.connectionsTo(self.switch)[0][1]
            bw = node.assigned_rx_bw / 1000000.0
            dst_intf.config(bw=bw)
            print "{tx}->{ap} downlink bandwidth = {bw}Mbps".format(tx=node.name, ap=self.name, bw=bw)

    def __repr__(self):
        return "ap name: {name} \n" \
               "\tactive_tx ues: {tx_ues}" \
               "\tactive_rx_ues: {rx_ues}".format(name=self.name, tx_ues=self.active_tx_ues,
                                                  rx_ues=self.active_rx_ues)


class TsaNet(Mininet):
    def __init__(self, *args, **kwargs):
        super(TsaNet, self).__init__(*args, **kwargs)
        self.tsa_hosts = []
        self.tsa_aps = []

    def add_ap(self, ap_name, pos, phy_model, **kwargs):
        ap = TsaAp(self, ap_name, pos, phy_model, **kwargs)
        self.tsa_aps.append(ap)
        return ap

    def add_tsa_host(self, host_name, pos, phy_model, **kwargs):
        tsa_host = TsaHost(self, host_name, pos, phy_model, **kwargs)
        self.tsa_hosts.append(tsa_host)
        return tsa_host