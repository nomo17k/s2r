#!/usr/bin/env python2.6
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
import numpy as np


def keeprange(fn):
    def _f(*args, **kwargs):
        r = fn(*args, **kwargs)
        if r == -1:
            return -1
        r = int(round(r))
        return r if 0 <= r <= 99 else (0 if r < 0 else 99)
    return _f


class Converter(object):

    def __init__(self, attr, stats):
        self.stats = stats
        self.attr = attr
        # {
        #     'FNM': '', 'LNM': '', 'HT': '', 'WT': -1, 'PO1': '', 'PO2': '',
        #     'T': '', 'B': '', 'USB': '',

        #     'STA': -1, 'PCL': -1, 'H9': -1, 'HR9': -1, 'K9': -1, 'BB9': -1,
        #     'P1': '', 'P1S': -1, 'P1C': -1, 'P1B': -1,
        #     'P2': '', 'P2S': -1, 'P2C': -1, 'P2B': -1,
        #     'P3': '', 'P3S': -1, 'P3C': -1, 'P3B': -1,
        #     'P4': '', 'P4S': -1, 'P4C': -1, 'P4B': -1,
        #     'P5': '', 'P5S': -1, 'P5C': -1, 'P5B': -1,

        #     'RCT': -1, 'LCT': -1, 'RPW': -1, 'LPW': -1, 'BNT': -1, 'DBN': -1,
        #     'VIS': -1, 'DIS': -1, 'CLU': -1, 'DUR': -1, 'SPD': -1, 'AMS': -1,
        #     'AMA': -1, 'REA': -1, 'FLD': -1, 'BLK': -1, 'BAB': -1, 'BAG': -1,
        # }

    def rate(self):
        a = self.attr
        a['K9'] = self.rate_k9()
        a['BB9'] = self.rate_bb9()
        a['H9'] = self.rate_h9()

        a['RCT'] = self.rate_contact()
        a['LCT'] = self.rate_contact()
        a['RPW'] = self.rate_power()
        a['LPW'] = self.rate_power()
        a['BNT'] = self.rate_buntingability()
        a['DBN'] = self.rate_dragbunting()
        a['VIS'] = self.rate_platevision()
        a['DIS'] = self.rate_platediscipline()
        a['CLU'] = self.rate_clutch()
        a['DUR'] = self.rate_durability()
        a['SPD'] = self.rate_speed()
        a['BAB'] = self.rate_brability()
        a['BAG'] = self.rate_braggressiveness()
        return a

    def rate_k9(self, *args, **kwargs): return -1
    def rate_bb9(self, *args, **kwargs): return -1
    def rate_h9(self, *args, **kwargs): return -1
    def rate_contact(self, *args, **kwargs): return -1
    def rate_power(self, *args, **kwargs): return -1
    def rate_buntingability(self, *args, **kwargs): return -1
    def rate_dragbunting(self, *args, **kwargs): return -1
    def rate_platevision(self, *args, **kwargs): return -1
    def rate_platediscipline(self, *args, **kwargs): return -1
    def rate_clutch(self, *args, **kwargs): return -1
    def rate_durability(self, *args, **kwargs): return -1
    def rate_speed(self, *args, **kwargs): return -1
    def rate_brability(self, *args, **kwargs): return -1
    def rate_braggressiveness(self, *args, **kwargs): return -1


class Basic(Converter):

    def rate(self):
        a = super(Basic, self).rate()
        a['RCT'] = self.rate_contact(bat=a['B'], vs='R', displ=a['DIS'])
        a['LCT'] = self.rate_contact(bat=a['B'], vs='L', displ=a['DIS'])
        a['RPW'] = self.rate_power(bat=a['B'], vs='R')
        a['LPW'] = self.rate_power(bat=a['B'], vs='L')
        a['SPD'] = self.rate_speed(pos=a['PO1'])
        return a

    @keeprange
    def rate_k9(self, *args, **kwargs):
        s = self.stats['pitching']
        so, out = s['SO'], s['IPOuts']
        if not (out > 0):
            return -1
        k9 = 27. * so / out
        return (k9 + 0.6519) / 0.1139

    @keeprange
    def rate_bb9(self, *args, **kwargs):
        s = self.stats['pitching']
        bb, tbf = s['BB'], s['BFP']
        if not (tbf > 0):
            return -1
        rr = bb / tbf
        return (rr - 0.1309) / -0.0007

    @keeprange
    def rate_h9(self, *args, **kwargs):
        s = self.stats['pitching']
        h, ab  = s['H'], s['BFP'] - s['BB'] -s['HBP'] -s['SF'] -s['SH']
        if not (ab > 0):
            return -1
        ba = h / ab
        return (ba - 0.3477) / -0.0014

    @keeprange
    def rate_contact(self, bat='R', vs='R', displ=40, psig=0., *args, **kwargs):
        s = self.stats['batting']
        h, ab = s['H'], s['AB']
        if not (ab > 0):
            return -1
        # generic ratio for (AB vs LHP) / (AB vs RHP)
        r = .50786 if bat == 'R' else 0.21818

        # platoon advantage: [(OBA vs LHP) - (OBA vs RHP)] / (OBA total)
        # for RHB.
        pltp = {'R': 0.0514, 'L': -0.0833, 'S': 0.0000}[bat]

        # std dev
        spltp = {'R': 0.0420, 'L': 0.0458, 'S': 0.0640}[bat]
        pltp += spltp * psig if bat == 'R' else -spltp * psig
        
        ba = (1.*h / ab * (1 + r * (1 - pltp)) / (1 + r) if vs == 'R'
              else (1.*h / ab * (r + 1 + pltp)) / (1 + r))
        return ((1. * ba - 0.1838 - 1.965e-4 * displ)
                / (1.034e-3 + 1.508e-6 * displ))

    @keeprange
    def rate_power(self, bat='R', vs='R', psig=0., *args, **kwargs):
        s = self.stats['batting']
        h, hr = s['H'], s['HR'] 
        if not (h > 0):
            return -1

        # generic ratio for (AB vs LHP) / (AB vs RHP)
        r = .50786 if bat == 'R' else 0.21818

        # platoon advantage: [(OBA vs LHP) - (OBA vs RHP)] / (OBA total)
        # for RHB.
        pltp = {'R': 0.0095, 'L': -0.0520, 'S': 0.000}[bat]
        
        # std dev
        spltp = {'R': 0.0420, 'L': 0.0458, 'S': 0.0640}[bat]
        pltp += spltp * psig if bat == 'R' else -spltp * psig

        hrph = (1.*hr / h * (1 + r * (1 - pltp)) / (1 + r) if vs == 'R'
                else (1.*hr / h * (r + 1 + pltp)) / (1 + r))
        return (hrph + 0.06375) / 3.350e-3

    @keeprange
    def rate_buntingability(self, *args, **kwargs):
        s = self.stats['batting']
        sh, pa = s['SH'], s['AB'] + s['BB'] + s['SH'] + s['SF'] + s['HBP']
        shpa = 1. * sh / pa / 12. if self.attr['PO1'] in ('SP','RP','CP') else 1.*sh/pa
        if not (pa > 0):
            return -1
        return 93. * (1. - np.exp(-80. * (shpa)))

    @keeprange
    def rate_dragbunting(self, *args, **kwargs):
        s = self.stats['batting']
        sh, pa = s['SH'], s['AB'] + s['BB'] + s['SH'] + s['SF'] + s['HBP']
        if not (pa > 0):
            return -1
        return 96. * (1. - np.exp(-60. * ((1. * sh / pa) - 0.002)))

    @keeprange
    def rate_platevision(self, *args, **kwargs):
        s = self.stats['batting']
        so, ab = s['SO'], s['AB']
        if not (ab > 0):
            return -1
        return - ((1. * so / ab) - 0.2884) / 1.6732e-3

    @keeprange
    def rate_platediscipline(self, *args, **kwargs):
        s = self.stats['batting']
        bb, pa = s['BB'], s['AB'] + s['BB'] + s['HBP'] + s['SH'] + s['SF']
        if not (pa > 0):
            return -1
        return (771.1 * (bb / pa))

    @keeprange
    def rate_clutch(self, *args, **kwargs):
        return 70.

    @keeprange
    def rate_durability(self, *args, **kwargs):
        s = self.stats['fielding']
        pf = (s['InnOuts'] / 3.) / (162. * 9. * s['YRS'])
        return ((pf + 1.97) / 0.03 if pf >= 0.88
                else ((pf - 0.5679) / 3.286e-3 if 0.65 <= pf < 0.88
                      else 66.))

    @keeprange
    def rate_speed(self, pos=None, *args, **kwargs):
        s = self.stats['batting']
        sb, cs = 1.*s['SB'], 1.*s['CS']
        h, h2, h3, hr = 1.*s['H'], 1.*s['2B'], 1.*s['3B'], 1.*s['HR']
        ab, so, bb = 1.*s['AB'], 1.*s['SO'], 1.*s['BB']
        r, hbp, gidp = 1.*s['R'], 1.*s['HBP'], 1.*s['GIDP']
        s = self.stats['fielding']
        po, a, g = 1.*s['PO'], 1.*s['A'], 1.*s['G']

        f1 = (sb + 3.0) / (sb + cs + 7.0)
        f1 = (f1 - 0.4) * 20.
        f2 = (sb + cs) / ((h - h2 - h3 - hr) + bb + hbp)
        f2 = np.sqrt(f2) / 0.07
        f3 = h3 / (ab - hr - so)
        f3 = f3 / 0.0016
        f4 = (r - hr) / (h + bb + hbp - hr)
        f4 = (f4 - 0.1) * 25.
        f5 = gidp / (ab - hr - so)
        f5 = (0.063 - f5) / 0.007
        f6 = {None: 0,
              'SP': 0., 'RP': 0., 'CP': 0.,
              'C': 1.,
              '1B': 2.,
              '2B': (((po + a) / g) / 4.8) * 6.,
              '3B': (((po + a) / g) / 2.65) * 4.,
              'SS': (((po + a) / g) / 4.6) * 7.,
              'LF': (((po + a) / g) / 2.0) * 6.,
              'CF': (((po + a) / g) / 2.0) * 6.,
              'RF': (((po + a) / g) / 2.0) * 6.}[pos]

        ss = np.array([float(f1), float(f2), float(f3), float(f4), float(f5),
                       float(f6)])
        ss[ss > 10] = 10.
        ss[ss < 0] = 0.
        ss = np.mean(ss, axis=0)
        return ((ss - 1.531) / 1.498e-3)**(1./1.822) if ss > 1.531 else 0.

    @keeprange
    def rate_brability(self, *args, **kwargs):
        s = self.stats['batting']
        sb, cs = s['SB'], s['CS']
        if not (sb + cs > 0):
            return -1
        sbp = 1. * sb / (sb + cs)
        return ((sbp * 100 - 52.3) / 0.3525)

    @keeprange
    def rate_braggressiveness(self, *args, **kwargs):
        s = self.stats['batting']
        sb, cs, h, bb, hbp = s['SB'], s['CS'], s['H'], s['BB'], s['HBP']
        if not (h + bb + hbp > 0):
            return -1
        sbr = 1. * (sb + cs) / (h + bb + hbp)
        return ((sbr + .02169) / 0.003397)
