#!/usr/bin/env python2.6
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
import csv
import os
from StringIO import StringIO
import numpy as np


DIRLAHMAN = '/home/taro/src/s2r/lahman58'


class LahmanReader(object):

    dtype = []
    internaldelimiter = '|'

    def __init__(self, filename):
        self.filename = filename
        self.data = self.read()

    def read(self, regeneratenpy=False):
        binfilename = self.filename[:-4] + '.npy'
        if not regeneratenpy and os.path.exists(binfilename):
            return np.load(binfilename)
    
        with open(self.filename) as f:
            reader = csv.reader(f, delimiter=',')

            s = StringIO()
            csvw = csv.writer(s, delimiter=self.internaldelimiter)
            r = [o for o in reader][1:]
            for o in r:
                csvw.writerow(o)
        s.seek(0)

        if 0:
            # find the max length for each field
            rr = np.array(r).transpose()
            for i, o in enumerate(rr):
                ss = 0
                for e in o:
                    ss = len(e) if len(e) > ss else ss
                print((self.dtype[i][0], ss))

        converters = {}
        for i, (name, dt) in enumerate(self.dtype):
            if dt.startswith('i'):
                converters[i] = lambda x: int(x or 0)
            elif dt.startswith('f'):
                converters[i] = lambda x: float(x or 0)
            elif dt.startswith('a'):
                converters[i] = lambda x: str(x)

        r = np.loadtxt(s, skiprows=0, delimiter=self.internaldelimiter,
                       dtype=self.dtype, converters=converters)
        s.close()
        np.save(binfilename, r)
        return r


class Master(LahmanReader):

    dtype = [('lahmanID', 'i'),
             ('playerID', 'a9'),
             ('managerID', 'a10'),
             ('hofID', 'a10'),
             ('birthYear', 'i'),
             ('birthMonth', 'i'),
             ('birthDay', 'i'),
             ('birthCountry', 'a24'),
             ('birthState', 'a2'),
             ('birthCity', 'a31'),
             ('deathYear', 'i'),
             ('deathMonth', 'i'),
             ('deathDay', 'i'),
             ('deathCountry', 'a34'),
             ('deathState', 'a2'),
             ('deathCity', 'a21'),
             ('nameFirst', 'a12'),
             ('nameLast', 'a14'),
             ('nameNote', 'a80'),
             ('nameGiven', 'a43'),
             ('nameNick', 'a48'),
             ('weight', 'f'),
             ('height', 'f'),
             ('bats', 'a1'),
             ('throws', 'a1'),
             ('debut', 'a18'),
             ('finalGamw', 'a18'),
             ('college', 'a40'),
             ('lahman40ID', 'a9'),
             ('lahman45ID', 'a9'),
             ('retroID', 'a8'),
             ('holtzID', 'a9'),
             ('bbrefID', 'a9')]

    def __init__(self, filename='%s/Master.csv' % DIRLAHMAN):
        super(Master, self).__init__(filename)


class Batting(LahmanReader):
    
    dtype = [("playerID", 'a9'),
             ("yearID", 'i'),
             ("stint", 'i'),
             ("teamID", 'a3'),
             ("lgID", 'a2'),
             ("G", 'i'),
             ("G_batting", 'i'),
             ("AB", 'i'),
             ("R", 'i'),
             ("H", 'i'),
             ("2B", 'i'),
             ("3B", 'i'),
             ("HR", 'i'),
             ("RBI", 'i'),
             ("SB", 'i'),
             ("CS", 'i'),
             ("BB", 'i'),
             ("SO", 'i'),
             ("IBB", 'i'),
             ("HBP", 'i'),
             ("SH", 'i'),
             ("SF", 'i'),
             ("GIDP", 'i'),
             ("G_old", 'i')]

    def __init__(self, filename='%s/Batting.csv' % DIRLAHMAN):
        super(Batting, self).__init__(filename)


class Pitching(LahmanReader):

    dtype = [("playerID", 'a9'),
             ("yearID", 'i'),
             ("stint", 'i'),
             ("teamID", 'a3'),
             ("lgID", 'a2'),
             ("W", 'i'),
             ("L", 'i'),
             ("G", 'i'),
             ("GS", 'i'),
             ("CG", 'i'),
             ("SHO", 'i'),
             ("SV", 'i'),
             ("IPOuts", 'i'),
             ("H", 'i'),
             ("ER", 'i'),
             ("HR", 'i'),
             ("BB", 'i'),
             ("SO", 'i'),
             ("BAOpp", 'f'),
             ("ERA", 'f'),
             ("IBB", 'i'),
             ("WP", 'i'),
             ("HBP", 'i'),
             ("BK", 'i'),
             ("BFP", 'i'),
             ("GF", 'i'),
             ("R", 'i'),
             ("SH", 'i'),
             ("SF", 'i'),
             ("GIDP", 'i')]

    def __init__(self, filename='%s/Pitching.csv' % DIRLAHMAN):
        super(Pitching, self).__init__(filename)


class Fielding(LahmanReader):

    dtype = [("playerID", 'a9'),
             ("yearID", 'i'),
             ("stint", 'i'),
             ("teamID", 'a3'),
             ("lgID", 'a2'),
             ("Pos", 'a2'),
             ("G", 'i'),
             ("GS", 'i'),
             ("InnOuts", 'i'),
             ("PO", 'i'),
             ("A", 'i'),
             ("E", 'i'),
             ("DP", 'i'),
             ("PB", 'i'),
             ("WP", 'i'),
             ("SB", 'i'),
             ("CS", 'i'),
             ("ZR", 'f')]

    def __init__(self, filename='%s/Fielding.csv' % DIRLAHMAN):
        super(Fielding, self).__init__(filename)
        
        # removing pos = 'OF' data, as they are duplicates of
        # individual outfield positions
        self.data = self.data[self.data['Pos'] != 'OF']

        # removing pos = 'DH' data, as they have no fielding stats
        self.data = self.data[self.data['Pos'] != 'DH']


class Appearances(LahmanReader):

    dtype = [("yearID", 'i'),
             ("teamID", 'a3'),
             ("lgID", 'a2'),
             ("playerID", 'a9'),
             ("UNKNOWN", 'i'),
             ("G_all", 'i'),
             ("G_start", 'i'),
             ("G_batting", 'i'),
             ("G_defense", 'i'),
             ("G_p", 'i'),
             ("G_c", 'i'),
             ("G_1b", 'i'),
             ("G_2b", 'i'),
             ("G_3b", 'i'),
             ("G_ss", 'i'),
             ("G_lf", 'i'),
             ("G_cf", 'i'),
             ("G_rf", 'i'),
             ("G_of", 'i'),
             ("G_dh", 'i')]

    def __init__(self, filename='%s/Appearances.csv' % DIRLAHMAN):
        super(Appearances, self).__init__(filename)






def main():
    m = Master().data
    b = Batting().data
    p = Pitching().data
    f = Fielding().data


    print(f)
    b = p

    lastname = 'nomo'

    idxs = []
    for i, o in enumerate(m):
        nl = o['nameLast'].lower()
        if nl.find(lastname) >= 0:
            idxs.append(o['playerID'])
    print(idxs)

    playerid = idxs[0]
    b = b[b['playerID'] == playerid]

    print(b)
    print("")

    m = np.zeros(b.size)
    for year in [1995, 1996, 1997]:
        m += (b['yearID'] == year)

    b = b[m.astype(bool)]
    print(b)
    print("")

    #t = b[['G', 'AB', 'HR']]
    t = b[['G', 'W', 'L']]

    print(t)

    ts = []
    for o in t:
        ts.append(list(o))
    t = np.array(ts)

    print(t.dtype)
    

    print(t.sum(axis=0))


    #t = np.array(b[['G', 'HR']], dtype='i')
    #print(t)
    #t = t.sum()
    #print(t)


if __name__ == '__main__':
    main()
