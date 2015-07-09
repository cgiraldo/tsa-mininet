# def simple_rssi_algorithm(tsaNet):
#
# for tsa_host in tsaNet.tsa_hosts:
# tsa_host.selected_ap =  tsa_host.atsanet[ue.params['phy_params'][0]['ap']]
# return selected_ap


def simple_tsa_algorithm(tsanet, ue):
    # initialize active users to the maximum possible value
    active_users = len(tsanet.tsa_hosts)
    selected_ap = ue.default_ap
    for candidate_params in ue.aps_phy_params:
        ap = candidate_params['ap']
        ap_active_users = len(ap.active_tx_ues) + len(ap.active_rx_ues)
        print 'checking candidate ' + ap.name + ' active users: ' + str(ap_active_users)
        if ap_active_users < active_users:
            selected_ap = ap
            active_users = ap_active_users
    print 'TSA algorithm selects ' + selected_ap.name + ' for ' + ue.name
    return selected_ap


def profiler_tsa_algorithm(tsanet, ue):
    # Same as simple tsa algorithm but we only consider active users the ones tx more than 500Kbps
    # FIXME we just put 10000 as 500Kbps/SCALE_BW assuming the scale factor is 50... but we don't have time for now
    # initialize active users to the maximum possible value
    active_users = len(tsanet.tsa_hosts)
    selected_ap = ue.default_ap
    for candidate_params in ue.aps_phy_params:
        ap = candidate_params['ap']
        ap_active_users = 0
        for tx_ue in ap.active_tx_ues:
            if tx_ue.required_tx_bw > 100000:
                ap_active_users += 1
        for rx_ue in ap.active_rx_ues:
            if rx_ue.required_rx_bw > 100000:
                ap_active_users += 1
        print 'checking candidate ' + ap.name + ' active users: ' + str(ap_active_users)
        if ap_active_users < active_users:
            selected_ap = ap
            active_users = ap_active_users
    print 'PROFILER algorithm selects ' + selected_ap.name + ' for ' + ue.name
    return selected_ap