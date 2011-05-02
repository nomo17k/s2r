#!/usr/bin/env python
import numarray as N
import numarray.records as NR
import numarray.strings as NS

from _progress_bar import ProgressBar

import csv
from mmap import mmap, MAP_PRIVATE, PROT_READ
from os import fstat


def reclist(file, verbose = True):
	f = open(file, mode = 'rt')
	fd = f.fileno()
	size = fstat(fd).st_size
	m = mmap(fd, size, MAP_PRIVATE, PROT_READ)
	f.close()

	factor = 1./1024.
	bar = ProgressBar(total = size * factor,
					  text = '%35s' % 'Mapping Lahman database 5.2:',
					  frac_fmt = '%.0f/%.0f')
	i = 0
	data = []
	while True:
		if verbose and i % 256 == 0:
			bar.done = m.tell() * factor
			bar.show()
		line = m.readline()
		if not line: break
		data.append(line)
		i += 1
	ret = csv.reader(data, dialect = 'excel')
	if verbose:
		bar.done = size * factor
		bar.show()
		print ''
	return ret, len(data)


def Master(file, verbose = True):
	names = 'lahmanID,playerID,managerID,hofID,birthYear,'\
			'birthMonth,birthDay,birthCountry,birthState,birthCity,'\
			'deathYear,deathMonth,deathDay,deathCountry,deathState,'\
			'deathCity,nameFirst,nameLast,nameNote,nameGiven,'\
			'nameNick,weight,height,bats,throws,'\
			'debut,college,lahman40ID,lahman45ID,retroID,'\
			'holtzID,bbrefID'

	rec, total = reclist(file, verbose)
	bar = ProgressBar(total = total,
					  text = '%35s' % 'Reading Master database:',
					  frac_fmt = '%.0f/%.0f')
	data = []
	i = 0
	for each in rec:
		if verbose:
			bar.done = i
			bar.show()
		i += 1
		if i == 1: continue
		if each[4] != '': birthYear = int(each[4])
		else: birthYear = -1
		if each[5] != '': birthMonth = int(each[5])
		else: birthMonth = -1
		if each[6] != '': birthDay = int(each[6])
		else: birthDay = -1
		if each[10] != '': deathYear = int(each[10])
		else: deathYear = -1
		if each[11] != '': deathMonth = int(each[11])
		else: deathMonth = -1
		if each[12] != '': deathDay = int(each[12])
		else: deathDay = -1
		if each[21] != '': weight = int(each[21])
		else: weight = -1
		if each[22] != '': height = int(each[22])
		else: height = -1
		data.append([int(each[0]), each[1], each[2], each[3], birthYear,
					 birthMonth, birthDay, each[7], each[8], each[9],
					 deathYear, deathMonth, deathDay, each[13], each[14],
					 each[15], each[16], each[17], each[18], each[19],
					 each[20], weight, height, each[23], each[24],
					 each[25], each[26], each[27], each[28], each[29],
					 each[30], each[31]])
	record = NR.array(data, names = names)
	if verbose:
		bar.done = total
		bar.show()
		print ''
	return record


def Batting(file, verbose = True):
	names = 'playerID,yearID,stintID,teamID,lgID,'\
			'G,AB,R,H,2B,'\
			'3B,HR,RBI,SB,CS,'\
			'BB,SO,IBB,HBP,SH,'\
			'SF,GIDP'
	rec, total = reclist(file, verbose)
	bar = ProgressBar(total = total,
					  text = '%35s' % 'Reading Batting database:',
					  frac_fmt = '%.0f/%.0f')
	i = 0
	data = []
	for each in rec:
		if verbose and i%256 == 0:
			bar.done = i
			bar.show()
		i += 1
		if i == 1: continue
		for j in xrange(5, len(each)):
			if each[j] != '': each[j] = int(each[j])
			else: each[j] = 0
		data.append([each[0], int(each[1]), int(each[2]), each[3], each[4],
					 each[5], each[6], each[7], each[8], each[9],
					 each[10], each[11], each[12], each[13], each[14],
					 each[15], each[16], each[17], each[18], each[19],
					 each[20], each[21]])
	record = NR.array(data, names = names)
	if verbose:
		bar.done = total
		bar.show()
		print ''
	return record


def Pitching(file, verbose = True):
	names = 'playerID,yearID,stintID,teamID,lgID,'\
			'W,L,G,GS,CG,'\
			'SHO,SV,IPouts,H,ER,'\
			'HR,BB,SO,BAOpp,ERA,'\
			'IBB,WP,HBP,BK,BFP,'\
			'GF,R'
	rec, total = reclist(file, verbose)
	bar = ProgressBar(total = total,
					  text = '%35s' % 'Reading Pitching database:',
					  frac_fmt = '%.0f/%.0f')
	data = []
	i = 0
	for each in rec:
		if verbose and i%256 == 0:
			bar.done = i
			bar.show()
		i += 1
		if i == 1: continue
		for j in xrange(5, 18):
			if each[j] != '': each[j] = int(each[j])
			else: each[j] = 0
		for j in (18, 19):
			if each[j] != '': each[j] = float(each[j])
			else: each[j] = -1.
		for j in xrange(20, len(each)):
			if each[j] != '': each[j] = int(each[j])
			else: each[j] = 0
		data.append([each[0], int(each[1]), int(each[2]), each[3], each[4],
					 each[5], each[6], each[7], each[8], each[9],
					 each[10], each[11], each[12], each[13], each[14],
					 each[15], each[16], each[17], each[18], each[19],
					 each[20], each[21], each[22], each[23], each[24],
					 each[20], each[21]])
	record = NR.array(data, names = names)
	if verbose:
		bar.done = total
		bar.show()
		print ''
	return record


#############
# Test Code
#############

if __name__ == '__main__':
	r = Master('./lahman52/Master.csv')
	b = Batting('./lahman52/Batting.csv')
	p = Pitching('./lahman52/Pitching.csv')
	print 'Good.'
	sarray = NS.array(r.field('nameLast'))
	tuple = sarray.search('Nomo')
	idx = tuple[0][0]
	playerID = r.field('playerID')[idx]


	sarray = NS.array(b.field('playerID'))
	tuple = sarray.search(playerID)

	print tuple
	for each in tuple[0]:
		print b[each]

	sarray = NS.array(p.field('playerID'))
	tuple = sarray.search(playerID)

	print tuple
	for each in tuple[0]:
		print p[each]
	
