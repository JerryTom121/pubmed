#!/usr/bin/python
import numpy as np
import pandas as pd


def getAuthorCount(st):
	if type(st) is str:
		return len(st.split("|"))
	return 0

def getAuthors(st):
	if type(st) is str:
		return st.split("|")
	return []

def getAuthorsAsDict(df):
	authors = set()
	for a in df.authors2.iteritems():
		b = a[1]
		for c in b:
			authors.add(c)
	return authors

def prepare():
	# df = pd.read_csv('publications-nov-2013-sample.csv')
	df = pd.read_csv('publications-nov-2013.csv')
	df['authorsCount'] = df.authors.map(getAuthorCount)
	df = df.dropna()
	df['authors2'] = df.authors.str.split("|")
	return df

def getAuthorsNumberOfPublications(df):
	from collections import defaultdict
	fq= defaultdict( int )
	li = []
	for authors in df.authors.iteritems():
		tmp = getAuthors(authors[1])
		if type(tmp) is list:
			li.extend(tmp)

	for l in li:
		fq[l] +=1

	rs = pd.DataFrame(fq.items())
	rs.rename(columns={0:'author'}, inplace=True)
	rs.rename(columns={1:'publications'}, inplace=True)
	rs = rs[rs.author!='']
	return rs

def getAuthorsFirstLastPub(df):
	authors  = getAuthorsAsDict(df)
	firstyear = dict.fromkeys(authors,2050)
	lastyear = dict.fromkeys(authors,0)

	i = 0
	for row in df.iterrows():
		i = i+1
		if i%100000==0:
			print i
		authors = row[1][5]
		year = row[1][2]
		if type(authors) is list:
			for author in authors:
				if (firstyear[author]>year):
						firstyear[author] = year
				if (lastyear[author]<year):
						lastyear[author] = year
	authors = pd.DataFrame(firstyear.items())
	authors.rename(columns={0:'author'}, inplace=True)
	authors.rename(columns={1:'firstyear'}, inplace=True)

	tmp = pd.DataFrame(lastyear.items())
	tmp.rename(columns={0:'author'}, inplace=True)
	tmp.rename(columns={1:'lastyear'}, inplace=True)
	tmp = tmp[tmp.author!='']
	authors = pd.merge(authors,tmp, left_on='author', right_on='author')
	return authors

def getLifeSpan(df):
	start = 1950
	step  = 5
	fl = getAuthorsFirstLastPub(df)
	pubs = getAuthorsNumberOfPublications(df)
	tmp = pd.merge(fl, pubs, left_on="author", right_on="author")
	while start<2010:
		decadeDF = tmp[(tmp.firstyear>=start)&(tmp.firstyear<start+step)]
		print str(start)+"'s\t" + str(decadeDF.publications.mean())
		start = start+step
	return tmp
