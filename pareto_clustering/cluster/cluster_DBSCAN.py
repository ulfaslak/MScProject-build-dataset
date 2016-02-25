from sklearn.cluster import DBSCAN
import numpy as np

def fit_clustering(D, params="auto"):
	"""Cluster traits given distance matrix D

	For practical purposes use inter-trait P-values as distance measures
	it works quite well. "auto" option scans parameters between shortest
	distance to longest distance, and smallest clusters to largest clusters
	for best solutions. Use it.

	Parameters
	----------
	D : numpy.ndarray
		M x M distance matrix where M is number of traits
	params : str/list
		Parameters for DBSCAN algorithm. If "auto" computes good values in the fly.

	Returns
	-------
	out : list
		DBSCAN cluster labels, ordered with respects to input distance matrix.
	"""

	if type(params) is list:
		eps, msa = params[0], params[1]
		db = DBSCAN(eps=eps, min_samples=msa, metric='precomputed')
		db.fit(D)
		labels = db.labels_

	elif params == "auto":

		vals = []
		for i in range(D.shape[0]):
		    for j in range(D.shape[1]):
		        if j <= i: continue
		        vals.append(D[i,j])


		eps_range = np.linspace(np.min(vals),np.max(vals),10)
		msa_range = range(2,12)

		# Construct grids of parameters vs number of clusters and outliers
		C = np.empty((10,10))
		O = np.empty((10,10))

		model_preds = {}

		for i in range(10):
			for j in range(10):
				eps = eps_range[i]
				msa = msa_range[j]

				db_ij = DBSCAN(eps=eps, min_samples=msa, metric='precomputed')
				db_ij.fit(D)
				labels = db_ij.labels_

				num_clusters = len(set([l for l in labels if l != -1]))
				num_outliers = len([1 for l in labels if l == -1])

				C[i,j] = num_clusters
				O[i,j] = num_outliers
				model_preds[(i,j)] = labels


		# Search grids for parameters giving maximal clusters and minimal outliers
		minimum_o = sorted(set(O.reshape(1,-1)[0]))
		maximum_c = sorted(set(C.reshape(1,-1)[0]),reverse=True)

		for i in maximum_c:
		    for j in minimum_o:
		        print int(i), "clusters and", int(j), "outliers"
		        min_ij = zip(*np.where(O == j))
		        max_ij = zip(*np.where(C == i))
		        best = set(max_ij) & set(min_ij)
		        if len(best) > 0:
		            params = sorted(best, key=lambda x: (x[0], x[1]))[0]
		            print "\t... found %d solutions, using minimal parameters eps=%.02f, min_samples=%d" % (
		                len(best),eps_range[params[0]],msa_range[params[1]])
		            break
		    else:
		        continue
		    break

		labels = model_preds[params]

	return labels

		
	
	

	return db.labels_