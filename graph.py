#!/usr/bin/python
import numpy as np
import pandas as pd
import networkx as nx

"""
http://eprints.pascal-network.org/archive/00001220/01/powergrowth-kdd05.pdf
First, most of these graphs densify over time, with the number of edges growing super- linearly in the number of nodes. Second, the average dis- tance between nodes often shrinks over time, in contrast to the conventional wisdom that such distance parameters should increase slowly as a function of the number of nodes (like O(log n) or O(log(log n)).
"""

def printStats(df):
	rs = pd.DataFrame()
	for year in df.pub_year.unique():
		tmp = df[df.pub_year==year]
		g = buildGraph(tmp)
		d = {}
		d['year'] = year
		d["#nodes"] = g.number_of_nodes()
		d["#edges"] = g.number_of_edges()
		d["clustering coefficient"] = nx.average_clustering(g)
		# h = nx.connected_component_subgraphs(g)[0]
		# d['diameter'] = nx.diameter(h)
		dist = centrality_distribution(g)
		d['entropy'] = entropy(dist)
		tmp = pd.Series.from_array(d)
		tmp = pd.DataFrame(tmp).transpose().set_index('year')
		rs = rs.append(tmp)
		print d
	return rs

def entropy(dist):
	"""
	Returns the entropy of `dist` in bits (base-2).
	motivated from http://www.lancaster.ac.uk/staff/rowem/files/mrowe-mstrohmaier-WWW2014-WebScience.pdf
	 In the context of our work, a higher entropy denotes greater graph density.
	"""
	dist = np.asarray(dist)
	ent = np.nansum( dist *  np.log2( 1/dist ) )
	return ent

def centrality_distribution(G):
	"""
	Returns a centrality distribution.

	Each normalized centrality is divided by the sum of the normalized
	centralities. Note, this assumes the graph is simple.

	"""
	centrality = nx.degree_centrality(G).values()
	centrality = np.asarray(centrality)
	centrality /= centrality.sum()
	return centrality


def buildGraph(df):
	import itertools
	import crunch
	authors = crunch.getAuthorsAsDict(df)
	g = nx.Graph()
	g.add_nodes_from(authors)
	for row in df.iterrows():
		authors = row[1][5]
		year = row[1][2]
		edges = list(itertools.combinations(authors, 2))
		if len(edges)>0:
			for edge in edges:
				g.add_edge(edge[0], edge[1],{'year':year})
			# print edges
		# break
	return g

def buildGraphByTopic(df, topic, decade):
	df3 = df[df.article_title.str.contains('stress')]
	df3 = df3[(df.pub_year>=decade)&(df.pub_year<decade+10)]

	g = buildGraph(df3)
	r = range(1,g.number_of_nodes())
	mapping=dict(zip(g.nodes(),r))
	h=nx.relabel_nodes(g,mapping)
	# nx.write_gexf(h, 'stress.gexf')
	return h
