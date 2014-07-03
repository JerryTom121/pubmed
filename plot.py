#!/usr/bin/python
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import sys
sys.path.insert(0, './text')
import topic
if not 'ddf' in locals():
	ddf = topic.batchPickle()

fs = (15,10)
fs = (5,3)
fsTopic = (15,5)
plt.xkcd()

def plotSNA():
	global fs
	df = pd.read_pickle('sna.pickle')
	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	df_min = df.reset_index()
	df_min = df_min[df_min['index']>1950]
	df_min = df_min[df_min['index']<2010]
	df_min.rename(columns={'index':'year'}, inplace=True)
	df_min = df_min.set_index('year')

	df_min['density'] = 2*df_min['#edges']
	df_min['density'] = df_min['density']/df_min['#nodes']
	df_min['density'] = df_min['density']/(df_min['#nodes']-1)

	df_min.rename(columns={'#nodes':'#authors'}, inplace=True)
	df_min.sort_index(inplace=True)
	ax1 = df_min['#authors'].plot(legend=True, logy=True)#, label="#nodes")
	plt.show()
	fig1.savefig('SNA-nodes.png', format='png',transparent=True)#, bbox_inches='tight')	

	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	df_min.rename(columns={'#edges':'#co-authorships'}, inplace=True)
	ax1 = df_min['#co-authorships'].plot(legend=True, logy=True, label="#co-authorships")
	plt.show()
	fig1.savefig('SNA-edges.png', format='png',transparent=True)#, bbox_inches='tight')	

	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	ax1 = df_min['clustering coefficient'].plot(legend=True, label="clustering coefficient")
	plt.show()
	fig1.savefig('SNA-clustering.png', format='png',transparent=True)#, bbox_inches='tight')	

	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	ax1 = df_min['entropy'].plot(legend=True, label="entropy")
	plt.show()
	fig1.savefig('SNA-entropy.png', format='png',transparent=True)#, bbox_inches='tight')	

	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	ax1 = df_min['density'].plot(legend=True, label="density")
	plt.show()
	fig1.savefig('SNA-density.png', format='png',transparent=True)#, bbox_inches='tight')	
	return df_min

def fetchTerm(term):
	global ddf
	d = {}
	for k in ddf.keys():
		df = ddf[k]	
		if len(df[df.term==term].pct.tolist())>0:
			d[k] = df[df.term==term].pct.tolist()[0]
		else:
			d[k] = 0
		df = pd.DataFrame.from_dict(d.items())
		df.rename(columns={0:'years'}, inplace=True)
		df.rename(columns={1:term}, inplace=True)
		df = df.set_index('years')
		df.sort_index(inplace=True)

	return df

def plotTopic(topics):
	global ddf
	global fs
	fig1 =plt.figure(dpi=360, figsize=fsTopic)
	ax1 = fig1.add_subplot(111)

	rs = pd.DataFrame()
	for t in topics:		
		kk = t.split("+")
		df = pd.DataFrame()		
		for k in kk:
			tmp = fetchTerm(k)
			tmp.rename(columns={k:t}, inplace=True)
			if len(df)>0:
				if len(kk)>1:
					df = df+tmp
				else:
					df = pd.merge(df,tmp, left_index=True, right_index=True)
			else:
				df = tmp
		

		ax1 = df[t].plot(legend=True, label="'"+t.replace('+',"' or '")+"'")
		if len(rs)>0:
			rs = pd.merge(rs,df, left_index=True, right_index=True)
		else:
			rs = df

	ax1.tick_params(pad=10)
	plt.show()
	fig1.savefig('Topics-'+'-'.join(topics)+'.png', format='png',transparent=True)
	return rs

def plotResearcherThroughput():
	global fs
	df = pd.read_pickle('lifespan.pickle')
	df = df[df.firstyear>=1965]
	tmp1 = df.groupby('firstyear')['duration'].mean()
	tmp1 = tmp1.reset_index()

	tmp2 = df.groupby('firstyear')['publications'].mean()
	tmp2 = tmp2.reset_index()

	rs = pd.merge(tmp1, tmp2, left_on='firstyear', right_on='firstyear')

	rs['throughput'] = rs['publications']/rs['duration']
	rs = rs.set_index('firstyear')
	rs = rs[rs.index<2002]
	
	fig1 =plt.figure(dpi=360, figsize=fs)
	ax1 = fig1.add_subplot(111)
	ax1 = rs['throughput'].plot(legend=True, label='Papers/year')
	fig1.savefig('Researcher-throughput.png', format='png',transparent=True)
	return rs

def plotResearcher():
	global fs
	df = pd.read_pickle('lifespan.pickle')
	df = df[df.firstyear>=1965]

	count = {}
	for year in df.firstyear.unique():
		count[int(year)] = len(df[df.firstyear==year])
	
	minDuration = 5

	df = df[df.duration>=minDuration]
	countDuration = {}
	for year in df.firstyear.unique():
		countDuration[int(year)] = len(df[df.firstyear==year])

	pct = {}
	for k in count.keys():
		if k<2009:
			pct[k] = countDuration[k]/float(count[k])

	tmp = pd.DataFrame(pct.items())
	tmp.rename(columns={0:'year'}, inplace=True)
	tmp.rename(columns={1:'percentage'}, inplace=True)
	tmp.percentage = tmp.percentage*100
	tmp = tmp.set_index('year')
	tmp = tmp[tmp.index<2002]

	fig1 =plt.figure(dpi=360, figsize=(10,3))
	ax1 = fig1.add_subplot(111)
	ax1 = tmp['percentage'].plot(legend=True, label='% of researchers with activity more than 5 years')

	plt.tight_layout()
	fig1.savefig('Researcher-pctMoreThan5years.png', format='png',transparent=True)

	return tmp

def plotGraph(df, year):
	import graph
	df1 = df[df.pub_year==year]
	graph = graph.buildGraph(df1)

	plt.figure(num=None, figsize=(20, 20), dpi=1000)
	plt.axis('off')
	fig = plt.figure(1)
	pos = nx.spring_layout(graph)
	nx.draw_networkx_nodes(graph,pos)
	nx.draw_networkx_edges(graph,pos)
	nx.draw_networkx_labels(graph,pos)
	cut = 1.00
	xmax = cut * max(xx for xx, yy in pos.values())
	ymax = cut * max(yy for xx, yy in pos.values())
	plt.xlim(0, xmax)
	plt.ylim(0, ymax)
	plt.show()
	plt.savefig('graph-'+str(year)+".pdf",bbox_inches="tight",format='pdf',transparent=True)
	return

def stackTopic(df):
	i = range(1950,2010,5)
	v = df.values.T
	plt.stackplot(i, v,baseline='wiggle')
	return

def plotBar():
	global fs

	fig = plt.figure(figsize=fs, dpi=1000)
	ax = fig.add_subplot(111)

	n_groups = 2

	means_men = (76213, 1783638)

	means_women = (61168, 10543316)

	fig, ax = plt.subplots()

	index = np.arange(n_groups)
	bar_width = 0.35

	opacity = 0.5

	rects1 = ax.bar(index, means_men, bar_width,
	                 alpha=opacity,
	                 color='b',
	                 log=True,
	                 label='Authors')

	rects2 = ax.bar(index + bar_width, means_women, bar_width,
	                 alpha=opacity,
	                 color='r',
	                 log=True,
	                 label='Co-authorships')

	plt.xlabel('Year')
	plt.ylabel('Size')
	plt.title('Authors vrs. co-authorships')
	plt.xticks(index + bar_width, ('1951', '2009'))
	plt.legend(loc=2, borderaxespad=0.)

	plt.tight_layout()
	plt.show()
	fig.savefig('SNA-Bar.png', format='png',transparent=True)
