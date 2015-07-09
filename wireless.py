import math
import random
import operator


class WirelessHost(object):
    def __init__(self, name, pos, phy_model, Pt=46, G_ant=25, noise_fig=5):
        self.name = name
        self.pos = pos
        self.Pt = Pt
        self.phy_model = phy_model
        self.G_ant = G_ant
        self.noise_fig = noise_fig


def distance(a, b):
    # TODO Check point a and b same dimension
    d2 = 0
    for i in range(len(a)):
        d2 = d2 + (a[i] - b[i]) * (a[i] - b[i])
    return math.sqrt(d2)


class PhyModel(object):
    def __init__(self, PL0, alpha, kT, W, pow_eff, bw_eff, max_se, shad_std=0, seed=1, bw_scale_factor=1.0):
        self.rand_gen = random.Random()
        self.rand_gen.seed(seed)
        self.n_hosts = 0
        self.PL0 = PL0
        self.alpha = alpha
        self.W = W
        self.shad_std = shad_std
        self.kT = kT
        self.pow_eff = pow_eff
        self.bw_eff = bw_eff
        self.max_se = max_se
        self.bw_scale = bw_scale_factor
        self.aps = []

    def register_ap(self, ap):
        self.aps.append(ap)

    def get_phy_params(self, ue):
        phy_params = []
        for ap in self.aps:
            phy_params.append(self._get_phy_params(ue, ap))
        rssi_ordered = sorted(phy_params, key=operator.itemgetter('ue_rssi'), reverse=True)
        return rssi_ordered

    def _get_phy_params(self, ue, ap):
        phy_params = dict()

        dist = distance(ue.pos, ap.pos)
        shadowing = 0 if self.shad_std == 0 else self.rand_gen.gauss(0, self.shad_std)
        # NOTE We consider identical shadowing realization for the uplink and the downlink channel
        path_loss = self.PL0 + self.alpha * 10 * math.log10(dist) + shadowing
        ue_rx_signal = ap.Pt + ap.G_ant + ue.G_ant - path_loss
        ap_rx_signal = ue.Pt + ue.G_ant + ap.G_ant - path_loss
        ue_rx_noise = self.kT + 10 * math.log10(self.W) + ue.noise_fig
        ap_rx_noise = self.kT + 10 * math.log10(self.W) + ap.noise_fig
        ue_rssi = ue_rx_signal + ue_rx_noise
        ap_rssi = ap_rx_signal + ap_rx_noise
        ue_SNRdB = ue_rx_signal - ue_rx_noise
        ue_SNR = math.pow(10, ue_SNRdB * 0.1)
        ap_SNRdB = ap_rx_signal - ap_rx_noise
        ap_SNR = math.pow(10, ap_SNRdB * 0.1)
        ue_se = min(math.log(1 + ue_SNR * self.pow_eff, 2), self.max_se)
        ap_se = min(math.log(1 + ap_SNR * self.pow_eff, 2), self.max_se)
        dl_bitrate = ue_se * self.bw_eff * self.W
        ul_bitrate = ap_se * self.bw_eff * self.W
        phy_params['ap'] = ap
        phy_params['distance'] = dist
        phy_params['shadowing'] = shadowing
        phy_params['pathloss'] = path_loss
        phy_params['ue_rssi'] = ue_rssi
        phy_params['ap_rssi'] = ap_rssi
        phy_params['dl_bitrate'] = dl_bitrate / self.bw_scale
        phy_params['ul_bitrate'] = ul_bitrate / self.bw_scale
        return phy_params