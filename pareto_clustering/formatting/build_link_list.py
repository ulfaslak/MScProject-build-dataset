import numpy as np

# if __name__ == '__main__':
# 	from os.path import abspath, dirname; import os
# 	PARENTDIR = abspath("../")
# 	os.sys.path.insert(0, PARENTDIR)

def build_from_P(P, ind=1, node_names=None, store=True):
	N, N = P.shape

	link_list = "*Vertices %d" % N

	if type(node_names) is list and len(node_names) == N:
		for i, f in enumerate(node_names):
			link_list += '\n%d "%s" 1.0' % ((i+ind), f)
	else:
		for i in range(N):
			link_list += '\n%d "Node %d" 1.0' % ((i+ind), (i+ind))

	link_list += "\n*Arcs %d" % (N*(N-1)/2)

	for i in range(N):
		for j in range(N):
			if j <= i: continue
			if P[i,j] >= 0.5: continue
			weight = -np.log2(P[i,j]+0.01) - 1.0+np.log2(1.02)
			link_list += "\n" + "%d %d %0.2f" % (i+ind, j+ind, weight)

	if store:
		print "Writing file 'link_listP.net'"
		with open('pareto_clustering/data_tmp/link_listP.net', 'w') as outfile:
			outfile.write(link_list)

	return link_list


def build_from_T(T, ind=1, node_names=None, store=True):
	N, N = T.shape

	link_list = "*Vertices %d" % N

	if type(node_names) is list and len(node_names) == N:
		for i, f in enumerate(node_names):
			link_list += '\n%d "%s" 1.0' % ((i+ind), f)
	else:
		for i in range(N):
			link_list += '\n%d "Node %d" 1.0' % ((i+ind), (i+ind))

	link_list += "\n*Arcs %d" % (N*(N-1)/2)

	for i in range(N):
		for j in range(N):
			if j <= i: continue
			if float("%0.2f" % T[i,j]) <= 1: continue
			weight = T[i,j] - 1
			link_list += "\n" + "%d %d %0.2f" % (i+ind, j+ind, weight)

	if store:
		print "Writing file 'link_listT.net'"
		with open('pareto_clustering/data_tmp/link_listT.net', 'w') as outfile:
			outfile.write(link_list)

	return link_list