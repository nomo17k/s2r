#!/usr/bin/env python2.6
"""
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
from optparse import OptionParser
import numpy as np
from s2r.lahman58 import Master, Pitching, Batting, Fielding, Appearances
from s2r.converter import Basic


__version__ = '20110428'


class NoPlayerFoundError(Exception): pass
class NoPlayingTimeError(Exception): pass


def outs2inn(outs):
    return ('%d.%d' % (outs // 3, outs % 3) if outs % 3 > 0
            else '%d  ' % (outs // 3))


def in2ft(inch):
    return '%d-%d' % (inch / 12., inch % 12)


def showstatspitching(pd):
    if pd.pitching.size == 0:
        return
    print("PITCHING")
    print()
    hdr = ('  YR AGE  TM LG'
           '   W   L    ERA   G  GS  CG  SV    IP'
           '      H    R   ER   HR   BB   SO')
    fmt = ('%4s %3.0f %3s %2s %3.0f %3.0f %6.2f %3.0f %3.0f %3.0f %3.0f %7s'
           ' %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f')

    print(hdr)
    print('-' * len(hdr))
    for o in pd.pitching:
        print(fmt % (o['yearID'],
                     pd.age(o['yearID']),
                     o['teamID'],
                     o['lgID'],
                     o['W'],
                     o['L'],
                     27. * o['ER'] / o['IPOuts'],
                     o['G'],
                     o['GS'],
                     o['CG'],
                     o['SV'],
                     outs2inn(o['IPOuts']),
                     o['H'],
                     o['R'],
                     o['ER'],
                     o['HR'],
                     o['BB'],
                     o['SO']))
        
    names = [n for n in pd.pitching.dtype.names[5:]]
    tot = compute_total(pd.pitching, names)

    # compute 162 G ave (following baseball-reference.com convention)
    n162 = 68. * np.array([list(o) for o in tot]) / (tot['G'] + tot['GS'])
    n162 = np.array([tuple(n162[0])], dtype=tot.dtype)
    
    def print_total(stats, label):
        p = stats
        print(('%15s' + fmt[17:])
              % (label,
                 p['W'],
                 p['L'],
                 27. * p['ER'] / p['IPOuts'],
                 p['G'],
                 p['GS'],
                 p['CG'],
                 p['SV'],
                 outs2inn(p['IPOuts']),
                 p['H'],
                 p['R'],
                 p['ER'],
                 p['HR'],
                 p['BB'],
                 p['SO'],
                 ))

    print('-' * len(hdr))
    print_total(tot, '%d Season Total' % o['YRS'])
    print_total(n162, '162 Game Ave.')


def showstatsbatting(pd):
    if pd.batting.size == 0:
        return
    print("BATTING")
    print()
    hdr = ('  YR AGE  TM LG'
           '    G    AB    R    H  2B  3B  HR  RBI'
           '  SB  CS   BB   SO'
           '   BA  OBP  SLG  OPS')
    fmt = ('%4s %3.0f %3s %2s'
           ' %4.0f %5.0f %4.0f %4.0f %3.0f %3.0f %3.0f %4.0f'
           ' %3.0f %3.0f %4.0f %4.0f'
           ' %4s %4s %4s %4s')
    
    def fmtrate(r):
        return (' ---' if r is None
                else (('%.3f' % r)[1:] if r < 1 else ('%.3f' % r)[:4]))

    def rate(x, y):
        return 1. * x / y if abs(y) > 0 else None

    print(hdr)
    print('-' * len(hdr))
    for o in pd.batting:
        ba = rate(o['H'], o['AB'])
        obp = rate(o['H'] + o['BB'] + o['HBP'],
                   o['AB'] + o['BB'] + o['HBP'] + o['SF'])
        slg = rate(o['H'] + 2. * o['2B'] + 3. * o['3B'] + 4. * o['HR'],
                   o['AB'])
        ops = None if None in (obp, slg) else obp + slg
        print(fmt
              % (o['yearID'], pd.age(o['yearID']), o['teamID'], o['lgID'],
                 o['G'],
                 o['AB'],
                 o['R'],
                 o['H'],
                 o['2B'],
                 o['3B'],
                 o['HR'],
                 o['RBI'],
                 o['SB'],
                 o['CS'],
                 o['BB'],
                 o['SO'],
                 fmtrate(ba),
                 fmtrate(obp),
                 fmtrate(slg),
                 fmtrate(ops)))

    names = [n for n in pd.batting.dtype.names[5:]]
    tot = compute_total(pd.batting, names)

    # compute 162 G ave (following baseball-reference.com convention)
    n162 = 162. * np.array([list(o) for o in tot]) / tot['G']
    n162 = np.array([tuple(n162[0])], dtype=tot.dtype)
    
    def print_total(stats, label):
        o = stats
        ba = rate(o['H'], o['AB'])
        obp = rate(o['H'] + o['BB'] + o['HBP'],
                   o['AB'] + o['BB'] + o['HBP'] + o['SF'])
        slg = rate(o['H'] + 2. * o['2B'] + 3. * o['3B'] + 4. * o['HR'],
                   o['AB'])
        ops = None if None in (obp, slg) else obp + slg
        print(('%15s' + fmt[17:])
              % (label,
                 o['G'],
                 o['AB'],
                 o['R'],
                 o['H'],
                 o['2B'],
                 o['3B'],
                 o['HR'],
                 o['RBI'],
                 o['SB'],
                 o['CS'],
                 o['BB'],
                 o['SO'],
                 fmtrate(ba),
                 fmtrate(obp),
                 fmtrate(slg),
                 fmtrate(ops)))

    print('-' * len(hdr))
    print_total(tot, '%d Season Total' % o['YRS'])
    print_total(n162, '162 Game Ave.')


def showstatsfielding(pd):
    if pd.fielding.size == 0:
        return
    print("FIELDING")
    print()
    hdr = ('  YR AGE  TM LG'
           ' POS    G   GS   INN      PO    A   E   DP'
           '  PB  WP   SB   CS')
    fmt = ('%4s %3.0f %3s %2s'
           ' %3s %4.0f %4.0f %7s %5.0f %4.0f %3.0f %4.0f'
           ' %3.0f %3.0f %4.0f %4.0f')

    print(hdr)
    print('-' * len(hdr))
    for o in pd.fielding:
        print(fmt
              % (o['yearID'], pd.age(o['yearID']), o['teamID'], o['lgID'],
                 o['Pos'],
                 o['G'],
                 o['GS'],
                 outs2inn(o['InnOuts']),
                 o['PO'],
                 o['A'],
                 o['E'],
                 o['DP'],
                 o['PB'],
                 o['WP'],
                 o['SB'],
                 o['CS']))

    names = [n for n in pd.fielding.dtype.names[6:]]
    tot = compute_total(pd.fielding, names)

    # compute 162 G ave (following baseball-reference.com convention)
    n162 = 162. * np.array([list(o) for o in tot]) / tot['G']
    n162 = np.array([tuple(n162[0])], dtype=tot.dtype)
    
    def print_total(stats, label):
        o = stats
        print(('%18s' + fmt[20:])
              % (label,
                 o['G'],
                 o['GS'],
                 outs2inn(o['InnOuts']),
                 o['PO'],
                 o['A'],
                 o['E'],
                 o['DP'],
                 o['PB'],
                 o['WP'],
                 o['SB'],
                 o['CS']))


    print('-' * len(hdr))
    print_total(tot, '%d Season Total' % o['YRS'])
    print_total(n162, '162 Game Ave.')


def showstatsappearances(pd):
    if pd.appearances.size == 0:
        return
    print("APPEARANCES")
    print()
    hdr = ('  YR AGE  TM LG'
           '    G   GS  BAT  DEF    P    C   1B   2B   3B   SS'
           '   LF   CF   RF   OF   DH')
    fmt = ('%4s %3.0f %3s %2s'
           ' %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f'
           ' %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f')

    print(hdr)
    print('-' * len(hdr))
    for o in pd.appearances:
        print(fmt
              % (o['yearID'], pd.age(o['yearID']), o['teamID'], o['lgID'],
                 o['G_all'],
                 o['G_start'],
                 o['G_batting'],
                 o['G_defense'],
                 o['G_p'],
                 o['G_c'],
                 o['G_1b'],
                 o['G_2b'],
                 o['G_3b'],
                 o['G_ss'],
                 o['G_lf'],
                 o['G_cf'],
                 o['G_rf'],
                 o['G_of'],
                 o['G_dh']))

    names = [n for n in pd.appearances.dtype.names[4:]]
    tot = compute_total(pd.appearances, names)

    # compute 162 G ave (following baseball-reference.com convention)
    n162 = 162. * np.array([list(o) for o in tot]) / tot['G_all']
    n162 = np.array([tuple(n162[0])], dtype=tot.dtype)
    
    def print_total(stats, label):
        o = stats
        print(('%15s' + fmt[17:])
              % (label,
                 o['G_all'],
                 o['G_start'],
                 o['G_batting'],
                 o['G_defense'],
                 o['G_p'],
                 o['G_c'],
                 o['G_1b'],
                 o['G_2b'],
                 o['G_3b'],
                 o['G_ss'],
                 o['G_lf'],
                 o['G_cf'],
                 o['G_rf'],
                 o['G_of'],
                 o['G_dh']))

    print('-' * len(hdr))
    print_total(tot, '%d Season Total' % o['YRS'])
    print_total(n162, '162 Game Ave.')


def compute_total(stats, columns, numtype='i'):
    if stats.size == 0:
        return stats
    # compute the number of seasons played
    nseason = np.unique(stats['yearID']).size
    
    dtype = [(str(c), numtype) for c in columns] + [('YRS', 'i')]
    tot = np.array([list(o) for o in stats[columns]]).sum(axis=0)
    tot = np.array([tuple(tot) + (nseason,)], dtype=dtype)
    return tot


class PlayerData(object):

    def __init__(self, playerid):
        self.playerid = playerid
        self._init()

    def _init(self):
        pid = self.playerid
        m = Master().data
        m = m[m['playerID'] == pid]
        if m.size == 0:
            s = ("No player found with the given ID: %s" % pid)
            raise NoPlayerFoundError(s)
        m = m[0]
        self.master = m
        p = Pitching().data
        self.pitching = p[p['playerID'] == pid]
        b = Batting().data
        self.batting = b[b['playerID'] == pid]
        f = Fielding().data
        self.fielding = f[f['playerID'] == pid]
        a = Appearances().data
        self.appearances = a[a['playerID'] == pid]

        self.attr = {
            'FNM': m['nameFirst'],
            'LNM': m['nameLast'],
            'HT': in2ft(m['height']),
            'WT': m['weight'],
            'PO1': '',
            'PO2': '',
            'T': m['throws'],
            'B': {'R': 'R', 'L': 'L', 'B': 'S'}[m['bats']],
            'USB': {True: 'Y', False: 'N'}[m['birthCountry'] == 'USA'],

            'STA': -1, 'PCL': -1, 'H9': -1, 'HR9': -1, 'K9': -1, 'BB9': -1,
            'P1': '', 'P1S': -1, 'P1C': -1, 'P1B': -1,
            'P2': '', 'P2S': -1, 'P2C': -1, 'P2B': -1,
            'P3': '', 'P3S': -1, 'P3C': -1, 'P3B': -1,
            'P4': '', 'P4S': -1, 'P4C': -1, 'P4B': -1,
            'P5': '', 'P5S': -1, 'P5C': -1, 'P5B': -1,

            'RCT': -1, 'LCT': -1, 'RPW': -1, 'LPW': -1, 'BNT': -1, 'DBN': -1,
            'VIS': -1, 'DIS': -1, 'CLU': -1, 'DUR': -1, 'SPD': -1, 'AMS': -1,
            'AMA': -1, 'REA': -1, 'FLD': -1, 'BLK': -1, 'BAB': -1, 'BAG': -1}

        self.update_total()

    def age(self, year):
        y, m = self.master['birthYear'], self.master['birthMonth']
        return (year - y - (m > 6))

    def trim_stats(self, years):
        ms = []
        for s in [self.pitching, self.batting, self.fielding, self.appearances]:
            m = np.zeros(s.size)
            for y in years:
                m += (s['yearID'] == y)
            ms.append(m.astype(bool))
        self.pitching = self.pitching[ms[0]]
        self.batting = self.batting[ms[1]]
        self.fielding = self.fielding[ms[2]]
        self.appearances = self.appearances[ms[3]]
        self.update_total()

    def update_total(self):
        statstotal = {}
        cols = [c for c in self.pitching.dtype.names[5:]]
        statstotal['pitching'] = compute_total(self.pitching, cols)
        cols = [c for c in self.batting.dtype.names[5:]]
        statstotal['batting'] = compute_total(self.batting, cols)
        cols = [c for c in self.fielding.dtype.names[6:]]
        statstotal['fielding'] = compute_total(self.fielding, cols)
        cols = [c for c in self.appearances.dtype.names[4:]]
        statstotal['appearances'] = compute_total(self.appearances, cols)
        if statstotal['appearances'].size == 0:
            raise NoPlayingTimeError('No apperance data found.')

        self.statstotal = statstotal

        # update attribute ratings
        self.attr['PO1'], self.attr['PO2'] = self.find_positions()

        c = Basic(self.attr, self.statstotal)
        self.attr = c.rate()

    def find_positions(self):
        posstr = ['P', 'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
        s = self.statstotal['appearances']
        gs = np.array([float(s['G_p']), float(s['G_c']), float(s['G_1b']),
                       float(s['G_2b']), float(s['G_3b']), float(s['G_ss']),
                       float(s['G_lf']), float(s['G_cf']), float(s['G_rf'])])
        if gs.sum() == 0:
            # likely a DH; need to decide from defensive spectrum
            return ('LF', '1B')

        idxsorted = np.argsort(gs)[::-1]
        pos1 = idxsorted[0]

        if pos1 == 0:
            # deal with a pitcher
            p = self.statstotal['pitching']
            if 1. * p['GS'] / p['G'] > .5:
                return ('SP', '')
            else:
                return ('CP' if p['SV'] > p['G'] * .3 else 'RP', '')

        if gs[idxsorted[1]] == 0:
            return (posstr[pos1], '')
        if gs[idxsorted[2]] == 0:
            return (posstr[pos1], posstr[idxsorted[1]])

        nif = gs[2:6].sum() if (gs[2:6] > 0).sum() == 4 else 0
        nof = gs[6:9].sum() if (gs[6:9] > 0).sum() == 3 else 0
        if nif > 0 and nif >= nof:
            return (posstr[pos1], 'IF')
        if nof > 0 and nof > nif:
            return (posstr[pos1], 'OF')
        if pos1 not in [3, 5] and gs[3] > 0 and gs[5] > 0:
            return (posstr[pos1], '2B/SS')
        if pos1 not in [2, 4] and gs[2] > 0 and gs[4] > 0:
            return (posstr[pos1], '1B/3B')
        if pos1 not in [1, 2] and gs[1] > 0 and gs[2] > 0:
            return (posstr[pos1], 'C/1B')
        if pos1 not in [1, 4] and gs[1] > 0 and gs[4] > 0:
            return (posstr[pos1], 'C/3B')
        return (posstr[pos1], posstr[idxsorted[1]])


    # ordered for generating csv output
    attrnames = ['FNM', 'LNM', 'HT', 'WT', 'PO1', 'PO2', 'T', 'B', 'USB',
                 'STA', 'PCL', 'H9', 'HR9', 'K9', 'BB9',
                 'P1', 'P1S', 'P1C', 'P1B', 'P2', 'P2S', 'P2C', 'P2B',
                 'P3', 'P3S', 'P3C', 'P3B', 'P4', 'P4S', 'P4C', 'P4B',
                 'P5', 'P5S', 'P5C', 'P5B',
                 'RCT', 'LCT', 'RPW', 'LPW', 'BNT', 'DBN', 'VIS', 'DIS', 'CLU',
                 'DUR', 'SPD', 'AMS', 'AMA', 'REA', 'FLD', 'BLK', 'BAB', 'BAG']

    def generate_csv(self):
        vs = []
        for n in self.attrnames:
            v = self.attr[n]
            if n in ['FNM', 'LNM', 'HT', 'PO1', 'PO2', 'T', 'B', 'USB',
                     'P1', 'P2', 'P3', 'P4', 'P5']:
                v = ('"%s"' % v)
            else:
                v = ('%d' % v)
            vs.append(v)
        return ','.join(vs)


def generate_csv(players, header=False):
    if header:
        print(','.join(PlayerData.attrnames))
    for pd in players:
        print(pd.generate_csv())


def showstats(pd):
    print()
    showstatspitching(pd)
    print()
    showstatsbatting(pd)
    print()
    showstatsfielding(pd)
    print()
    showstatsappearances(pd)


def showfulloutput(pd):
    attr = pd.attr
    
    print('FNM        LNM           HT   WT    PO1  PO2     T  B    USB')
    print('%(FNM)-10s %(LNM)-10s %(HT)5s  %(WT)3d   %(PO1)4s %(PO2)4s'
          '     %(T)1s  %(B)1s      %(USB)1s'
          % attr)
    print()

    if attr['PO1'] in ['SP', 'RP', 'CP']:
        print('STA  PCL   H9  HR9   K9  BB9')
        print(' %(STA)2d   %(PCL)2d   %(H9)2d   %(HR9)2d   %(K9)2d   %(BB9)2d'
              % attr)
        print()

        h = ''
        s = ''
        for i in range(1, 6):
            key = 'P%d' % i
            if len(attr[key]) == 0:
                continue
            h += '  P%d P%dS P%dC P%dB ' % (i, i, i, i)
            s += ('%4s  %2d  %2d  %2d '
                  % (attr[key], attr[key + 'S'], attr[key +'C'],
                     attr[key + 'B']))
        if h and s:
            print(h)
            print(s)
            print()

    print('RCT  LCT  RPW  LPW  BNT  DBN  VIS  DIS'
          '  CLU  DUR  SPD  AMS  AMA  REA  FLD  BLK  BAB  BAG')
    print(' %(RCT)2d   %(LCT)2d   %(RPW)2d   %(LPW)2d   %(BNT)2d   %(DBN)2d   %(VIS)2d   %(DIS)2d'
          '   %(CLU)2d   %(DUR)2d   %(SPD)2d   %(AMS)2d   %(AMA)2d   %(REA)2d   %(FLD)2d   %(BLK)2d   %(BAB)2d   %(BAG)2d'
          % attr)


def search(searchword, simple=False, maxplayer=20):
    """
    Search player name in the database and list player IDs found.
    """
    searchword = searchword.lower()
    m = Master().data

    idxs = []
    for i, o in enumerate(m):
        nl = (' '.join([o['nameFirst'], o['nameLast']])).lower()
        if nl.find(searchword) >= 0:
            idxs.append(o['playerID'])

    if simple:
        ps = []
        for idx in idxs:
            p = m[m['playerID'] == idx][0]
            ps.append(p['playerID'])
        print(' '.join(ps))
        return

    if len(idxs) == 0:
        print('No players found.')
        return
    elif len(idxs) > maxplayer:
        print('More than %d players found.  Listing first %d players.'
              % (maxplayer, maxplayer))
        print('')
        idxs = idxs[:maxplayer]

    def justyear(s):
        i = s.find(' ')
        return s[:i][-4:]

    fmt = '%-9s  %-20s  %10s    %-20s'
    header = (fmt % ('Player ID', 'Full Name', 'Born', 'Years Active'))
    print(header)
    print('-' * len(header))
    for idx in idxs:
        p = m[m['playerID'] == idx][0]
        yac = justyear(p['debut']) + ' - ' + justyear(p['finalGamw'])
        print(fmt
              % (p['playerID'],
                 ' '.join([p['nameFirst'], p['nameLast']]),
                 p['birthYear'],
                 yac))


def main(pids, opts):
    players = []
    for pid in pids:
        try:
            pd = PlayerData(pid)
        except NoPlayerFoundError:
            print("%s not found in database. Skipping." % pid)
            continue
        except:
            print("Error reading %s. Skipping." % pid)
            continue
        if len(opts.year):
            try:
                pd.trim_stats([int(y) for y, w in opts.year])
            except NoPlayingTimeError:
                print("No playing time found for %s. Skipping." % pd.playerid)
                continue
        players.append(pd)

    if opts.csv:
        generate_csv(players, header=opts.csvheader)
    else:
        maxcharwidth = 95
        print()
        print('=' * maxcharwidth)
        print(' ' * 25 + "MLB 11 THE SHOW PLAYER ATTRIBUTE RATINGS")

        for pd in players:
            print('=' * maxcharwidth)
            print()
            showfulloutput(pd)
            if opts.stats:
                showstats(pd)
            print()


if __name__ == '__main__':
    usage = '%prog [OPTIONS] PLAYERID1 [PLAYERID2 ...]'
    p = OptionParser(usage=usage, description=__doc__.strip(),
                     version=__version__)
    p.add_option('--csv', action='store_true', default=False,
                 help='generate a csv line')
    p.add_option('--csvheader', action='store_true', default=False,
                 help='generate a csv header line')
    p.add_option('-s', '--search', nargs=1, default=False,
                 help='search player name in Lahman database')
    p.add_option('--stats', action='store_true', default=False,
                 help='show stats for a player')
    p.add_option('-y', '--year', nargs=2, action='append', default=[],
                 help='year to use and weight given')
    p.add_option('--simple', action='store_true', default=False,
                 help='simplified output')

    opts, args = p.parse_args()

    if opts.search:
        if len(opts.search) < 2:
            p.error("Search word must be two chars or more.")
        search(opts.search, simple=opts.simple)
    else:
        if len(args) == 0:
            import sys
            args = sys.stdin.read().split()
            if len(args) == 0:
                p.error("Need a player ID.")
        pids = args
        main(pids, opts)
        
