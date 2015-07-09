import matplotlib.collections as mc
import matplotlib.pyplot as plt


def represent_network(net):
    ue_pos = []
    ue_type2_pos = []
    host_pos = []
    ap_pos = []
    switch_pos = []
    link_lines = []
    wireless_lines = []
    wireless_type2_lines = []
    for host in net.hosts:
        if 'isUe' in host.params:
            if host.params['type'] == 1:
                ue_pos.append(host.params['pos'])
            elif host.params['type'] == 2:
                ue_type2_pos.append(host.params['pos'])
        else:
            host_pos.append(host.params['pos'])
    for switch in net.switches:
        if 'isAp' in switch.params:
            ap_pos.append(switch.params['pos'])
        elif 'isUe' in switch.params:
            pass
            # ue_pos.append(switch.params['pos'])
        else:
            switch_pos.append(switch.params['pos'])
    for link in net.links:
        node1 = link.intf1.node
        node2 = link.intf2.node
        if 'isUe' in node1.params:
            if node1.params['type'] == 1:
                wireless_lines.append([link.intf1.node.params['pos'], link.intf2.node.params['pos']])
            elif node1.params['type'] == 2:
                wireless_type2_lines.append([link.intf1.node.params['pos'], link.intf2.node.params['pos']])
        elif 'isUe' in node2.params:
            if node2.params['type'] == 1:
                wireless_lines.append([link.intf1.node.params['pos'], link.intf2.node.params['pos']])
            elif node2.params['type'] == 2:
                wireless_type2_lines.append([link.intf1.node.params['pos'], link.intf2.node.params['pos']])
        else:
            link_lines.append([link.intf1.node.params['pos'], link.intf2.node.params['pos']])
    plt.plot(zip(*ue_pos)[0], zip(*ue_pos)[1], 'g^', ms=20)
    plt.plot(zip(*ue_type2_pos)[0], zip(*ue_type2_pos)[1], 'r^', ms=20)
    plt.plot(zip(*host_pos)[0], zip(*host_pos)[1], 'b^', ms=20)
    plt.plot(zip(*ap_pos)[0], zip(*ap_pos)[1], 'gs', ms=20)
    plt.plot(zip(*switch_pos)[0], zip(*switch_pos)[1], 'bs', ms=20)
    lc = mc.LineCollection(link_lines, linewidths=3, facecolor='blue')
    wlc = mc.LineCollection(wireless_lines, linewidths=1, facecolor='green')
    wlc2 = mc.LineCollection(wireless_type2_lines, linewidths=1, facecolor='red')
    ax = plt.axes()
    ax.add_collection(lc)
    ax.add_collection(wlc)
    ax.add_collection(wlc2)
    ax.margins(0.1)
    plt.show()
