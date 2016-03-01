from sklearn.cluster import DBSCAN
import numpy as np

def fit_clustering(D, mat="P", params="auto", visualize=False):
	"""Cluster traits given distance matrix D

	For practical purposes use inter-trait P-values as distance measures
	it works quite well. "auto" option scans parameters between shortest
	distance to longest distance, and smallest clusters to largest clusters
	for best solutions. Use it.

	Parameters
	----------
	D : numpy.ndarray
		M x M distance matrix where M is number of traits
	mat : str
		Indication about whether clustering is performed for the P or T matrix.
		Default entry is "P", other option is "T".
	params : str/list
		Parameters for DBSCAN algorithm. If "auto" computes good values in the fly.

	Returns
	-------
	out : list
		DBSCAN cluster labels, ordered with respects to input distance matrix.
	"""

	N, N = D.shape
	D_eff = np.empty((N,N))

	# Apply transformations
	if mat == "P":
		for i in range(N):
			for j in range(N):
				if j <= i: continue
				if D[i,j] >= 0.5:
					dist = np.inf
				else:
					dist = -np.log2((0.5-D[i,j])+0.01) - 1.0+np.log2(1.02)
				D_eff[i,j] = dist
				D_eff[j,i] = dist

	elif mat == "T":
		for i in range(N):
			for j in range(N):
				if j <= i: continue
				if D[i,j] <= 1: 
					dist = np.inf
				else:
					dist = 1.0/(D[i,j] - 1)
				D_eff[i,j] = dist
				D_eff[j,i] = dist

	# Read parameters and go
	if type(params) is list:
		eps, msa = params[0], params[1]
		db = DBSCAN(eps=eps, min_samples=msa, metric='precomputed')
		db.fit(D_eff)
		labels = db.labels_

	elif params == "auto":
		vals = []
		for i in range(N):
		    for j in range(N):
		        if j <= i: continue
		        if D_eff[i,j] != np.inf:
		        	vals.append(D_eff[i,j])


		eps_range = np.linspace(np.min(vals)+0.0001,np.median(vals)+0.0001,10)
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
				db_ij.fit(D_eff)
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
		        min_ij = zip(*np.where(O == j)) # [(1,2),(1,3),(2,5)]
		        max_ij = zip(*np.where(C == i)) # [(1,3),(2,5),(6,7)]
		        best = set(max_ij) & set(min_ij) # {(1,2),(2,5)}
		        if len(best) > 0:
		            params = sorted(best, key=lambda x: (x[0], x[1]))
		            min_params = params[0]
		            print "\t... found %d valid solutions, using eps=%f, min_samples=%d (minimal params)" % (
		                len(best),eps_range[min_params[0]],msa_range[min_params[1]])
		            break
		    else:
		        continue
		    break

		labels = model_preds[min_params]

		if visualize:
			import pandas as pd; import seaborn as sns; import matplotlib.pylab as plt
			plt.figure(figsize=(16,6))

			plt.subplot(1,2,1)
			plt.title("Number of clusters", fontsize=16)
			sns.heatmap(pd.DataFrame(C),cmap="cool")

			plt.subplot(1,2,2)
			plt.title("Number of outliers", fontsize=16)
			sns.heatmap(pd.DataFrame(O),cmap="cool")

			plt.show()
	return labels