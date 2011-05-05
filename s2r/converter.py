#!/usr/bin/env python2.6
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals


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
        a['VIS'] = self.rate_platevision()
        a['DIS'] = self.rate_platediscipline()
        a['BAB'] = self.rate_brability()
        a['BAG'] = self.rate_braggressiveness()
        return a

    def rate_k9(self, *args, **kwargs): return -1
    def rate_bb9(self, *args, **kwargs): return -1
    def rate_h9(self, *args, **kwargs): return -1
    def rate_contact(self, *args, **kwargs): return -1
    def rate_power(self, *args, **kwargs): return -1
    def rate_platevision(self, *args, **kwargs): return -1
    def rate_platediscipline(self, *args, **kwargs): return -1
    def rate_brability(self, *args, **kwargs): return -1
    def rate_braggressiveness(self, *args, **kwargs): return -1


class Basic(Converter):

    def rate(self):
        a = super(Basic, self).rate()
        a['RCT'] = self.rate_contact(bat=a['B'], vs='R', displ=a['DIS'])
        a['LCT'] = self.rate_contact(bat=a['B'], vs='L', displ=a['DIS'])
        a['RPW'] = self.rate_power(bat=a['B'], vs='R')
        a['LPW'] = self.rate_power(bat=a['B'], vs='L')
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
        
        ba = (h / ab * (1 + r * (1 - pltp)) / (1 + r) if vs == 'R'
              else (h / ab * (r + 1 + pltp)) / (1 + r))
        print(('ba=',ba))
        return ((1. * ba) - 0.1896) / (8.467e-4 + 5.488e-6 * displ)

    @keeprange
    def rate_power(self, bat='R', vs='R', psig=0., *args, **kwargs):
        s = self.stats['batting']
        h, hr, ab = s['H'], s['HR'], s['AB']
        if not (ab > 0 and h > 0):
            return -1

        # generic ratio for (AB vs LHP) / (AB vs RHP)
        r = .50786 if bat == 'R' else 0.21818

        # platoon advantage: [(OBA vs LHP) - (OBA vs RHP)] / (OBA total)
        # for RHB.
        pltp = {'R': 0.0095, 'L': -0.0520, 'S': 0.000}[bat]
        
        # std dev
        spltp = {'R': 0.0420, 'L': 0.0458, 'S': 0.0640}[bat]
        pltp += spltp * psig if bat == 'R' else -spltp * psig

        hpab = (hr / ab * (1 + r * (1 - pltp)) / (1 + r) if vs == 'R'
              else (hr / ab * (r + 1 + pltp)) / (1 + r))
        print(('pow=', hpab * ab / h))

        return 550. * (1. * hpab) / 0.5844 + 25.

    @keeprange
    def rate_platevision(self, *args, **kwargs):
        s = self.stats['batting']
        so = s['SO']
        ab = s['AB']
        if not (ab > 0):
            return -1
        return 164.7 - 558.8 * (so / ab)

    @keeprange
    def rate_platediscipline(self, *args, **kwargs):
        s = self.stats['batting']
        bb = s['BB']
        pa = s['AB'] + s['BB'] + s['HBP'] + s['SH'] + s['SF']
        if not (pa > 0):
            return -1
        return (771.1 * (bb / pa))

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
