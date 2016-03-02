from pareto_clustering.dependencies.point_location import min_triangle as mint
from pareto_clustering.dependencies.point_location.geo.shapes import Point, Polygon
from pareto_clustering.dependencies.point_location.geo.spatial import toNumpy, convexHull
from pareto_clustering.dependencies.point_location.geo.drawer import plot
from build_dataset.analysis.outlier_detection import Outlier_detector_svm

import numpy as np
from datetime import datetime as dt
import signal
import matplotlib.pylab as plt
from matplotlib.patches import Ellipse


class TimeoutException(Exception):   # Custom exception class
	pass

def timeout_handler(signum, frame):   # Custom signal handler
	raise TimeoutException

class Build_S:
	"""Build P (p-value distance matrix) and T (T-ratio similarity matrix)
	
	Computes p-values and T-ratios for trait pairs, following a bootstrapping
	scheme that enforces consistency in subsets chosen across trait pairs
	(see use of list 'subsets' in code below). Uses an implementation
	of minimal enclosing triangle computation [O'Rourke 86]. Some of the 
	trait pairs have boundaries at which most datapoints lie, causing the 
	algorithm to converge extremely slow, when the chosen subset contains 
	a lot of points on the boundary. It happens because the minimal enclosing 
	triangle must must enclose a very "narrow" and "tall" set of points, 
	causing the length of one edge to go towards infinity. To deal with this 
	inevitable problem, a timeout condition is established, killing triangle 
	computations taking longer than 200 milliseconds. This means that some 
	of the p-values are computed from a smaller number of iterations, but it 
	does not result in significantly worse results.

	It should be stated that estimating triangularness using this approach is
	SENSITIVE to datadistributions with narrow convex hulls, where the triangle
	enclosing the original data can grow extremely wide/tall, rendering the area
	of the shuffled data triangle smaller, even though it is in fact less triangular.
	
	Triangle computation has TC O(N*log(N)) and the implementation in this class
	(without regards for triangle computation) has TC O(M^2*num_iter), so effective
	TC should be O(M^2*num_iter*Ns*log(Ns)), where Ns is N*sample_size.
	
	Parameters
	----------
	X : numpy.ndarray
		N x M matrix where N is samples and M is traits
	num_iter : int
		Number of bootstrapping iterations
	sample_size : float
		0 < sample_size <= 1 denotes the fraction of N points used in each
		bootstrapping iterations. Governs the trait-off between accurate data
		geometry modeling with high sensitivity to outliers (high) and poor data
		geometry modeling with low sensitibity to outliers (low). 0.6 is a good
		choise for the Sensible DTU dataset (becomes unstable below this value).
	remove_outliers : bool/dict
		Whether or not to remove outliers indenpendently for each traitpair before
		computing p-values and T-ratios. If 'True' is provided it uses default
		OneClass SVM novelty detection parameters. A dictionary can also be provided
		with custom arguments such as: {'nu':0.1,'threshold':0,'gamma':0.25}.
		
	Returns
	-------
	P : numpy.ndarray
		M x M matrix of trait-pair triangle-p-values
	T : numpy.ndarray
		M x M matrix of trait-pair triangle-T-ratios
	"""

	def __init__(self, X, num_iter=100,sample_size=0.5, remove_outliers=True):
		self.X_orig = X
		self.N, self.M = X.shape
		self.num_iter = num_iter
		self.sample_size = sample_size
		self.remove_outliers = remove_outliers
		self.Nsubset = int(self.N*sample_size)

		if not remove_outliers:
			pass
		elif remove_outliers == True:
			params = {'threshold': -1, 'nu': 0.1, 'gamma': 0.25}
		elif type(remove_outliers) is dict and set(remove_outliers.keys()) == set(['threshold', 'nu', 'gamma']):
			self.remove_outliers = True
			params = remove_outliers
		else:
			print "'remove_outliers' format is incorrect. Using default params."
			self.remove_outliers = True
			params = {'threshold': -1, 'nu': 0.1, 'gamma': 0.25}

		# Change the behavior of SIGALRM
		signal.signal(signal.SIGALRM, timeout_handler)


	def __clean_Xpair(self,Xpair):
		"""Return pointset with outliers removed
		"""
		if self.remove_outliers:
			out_svm = Outlier_detector_svm(Xpair, hard=False, threshold=-1, visualize=False, nu=0.1, gamma=0.25)
			outliers = out_svm.main()
			inliers = list(set(range(Xpair.shape[0]))-set(outliers))
			return np.delete(Xpair,outliers,axis=0), outliers, inliers
		else:
			return Xpair, [], range(Xpair.shape[0])


	def __min_tri(self, Xpair):
		"""Compute min. triangle for set of points
		"""
		while True:
			points = [Point(*tuple(p)) for p in Xpair]
			min_tri = mint.minTriangle(Polygon(points))
			area = min_tri.area()

			# To correct for occational faulty "super small" area computed.
			# In effect calling continue on the loop will cause the operation
			# to timeout, and the subset to be skipped in bootstrapping.
			if area < 0.001: continue

			break

		return points, min_tri, area



	def _build_S(self, visualize):

		# Number of pairs to compute
		num_pairs = self.M*(self.M-1)/2

		# Triangle computation time allowed
		patience = 0.2

		P = np.zeros((self.M, self.M))
		T = np.zeros((self.M, self.M))
		C = np.zeros((self.M, self.M))

		compute_area = lambda P: abs((P[0]*(P[3]-P[5]) + P[2]*(P[5]-P[1]) + P[4]*(P[1]-P[3])) / 2.0)
		compute_dist = lambda (P1,P2): np.sqrt((P1[0]-P2[0])**2 + (P1[1]-P2[1])**2)

		pair_triangles_orig = {}
		pair_triangles_shuf = {}

		pair_inliers = {}
		pair_outliers = {}

		p = 0; c = 0
		for i in range(self.M):
			#print i, "vs...",
			for j in range(self.M):
				if j <= i: continue
				if int(c*1.0/num_pairs*100) > p:
					print "%d%% %d/%d" % (p, c,num_pairs); p+=10
				c += 1

				Xpair_cleaned, outliers, inliers = self.__clean_Xpair(self.X_orig[:,[i,j]])
				pair_inliers[(i,j)] = inliers
				pair_outliers[(i,j)] = outliers

				Xpair_orig = Xpair_cleaned
				Xpair_shuf = Xpair_orig.copy()
				for k in range(2):
					np.random.shuffle(Xpair_shuf[:,k])

				Npair, Mpair = Xpair_orig.shape

				areas_s_mintri_orig = []
				areas_s_convex_orig = []
				areas_s_mintri_shuf = []
				areas_s_convex_shuf = []

				tri_points_s_orig = np.empty((6,self.num_iter))
				tri_points_s_shuf = np.empty((6,self.num_iter))

				# Bootstrapping
				t = 0
				loop_over = range(self.num_iter)
				for n in loop_over:
					subset_indices = np.random.randint(0,Npair,size=int(self.Nsubset))

					Xpair_s_orig = Xpair_orig[subset_indices,:]
					Xpair_s_shuf = Xpair_shuf[subset_indices,:]

					time_start = dt.now()
					signal.setitimer(signal.ITIMER_REAL,patience)
					try:
						# Minimal triangles
						failed = "orig"
						points_s_orig, min_tri_s_orig, tri_s_area_orig = self.__min_tri(Xpair_s_orig)
						failed = "shuf"
						points_s_shuf, min_tri_s_shuf, tri_s_area_shuf = self.__min_tri(Xpair_s_shuf)
						signal.alarm(0)
						patience = 1.5*(dt.now()-time_start).total_seconds()
					except ValueError: 
						t+=1
						signal.alarm(0)
						loop_over.append(self.num_iter-1+t)
						continue
					except TimeoutException: 
						t+=1
						loop_over.append(self.num_iter-1+t)
						continue
					except AttributeError:
						print "Failed for: %s" % failed
						plt.figure(figsize=(6,6))
						plt.title("Distribution of points for which mintri calc fails")
						if failed == "orig":
							plt.scatter(Xpair_s_orig[:,0], Xpair_s_orig[:,1])
							plt.show()
						else:
							plt.scatter(Xpair_s_shuf[:,0], Xpair_s_shuf[:,1])
							plt.show()

					# Convex hull area
					convexarea_orig = convexHull(points_s_orig).area()
					convexarea_shuf = convexHull(points_s_shuf).area()

					areas_s_mintri_orig.append(tri_s_area_orig)
					areas_s_convex_orig.append(convexarea_orig)
					areas_s_mintri_shuf.append(tri_s_area_shuf)
					areas_s_convex_shuf.append(convexarea_shuf)

					tri_points_s_orig[:,n-t] = toNumpy(min_tri_s_orig.points).reshape((6,1)).T
					tri_points_s_shuf[:,n-t] = toNumpy(min_tri_s_shuf.points).reshape((6,1)).T

				P[i,j] = np.mean(np.array(areas_s_mintri_orig) >= np.array(areas_s_mintri_shuf))
				T[i,j] = np.mean(areas_s_mintri_shuf) / np.mean(areas_s_mintri_orig)
				C[i,j] = np.mean(areas_s_convex_orig) / np.mean(areas_s_convex_shuf)

				if visualize:
					pair_triangles_orig[(i,j)] = tri_points_s_orig.T.reshape(-1,2)
				#print "%d(%d)" % (j,t),
			#print

		print "100%% %d/%d" % (num_pairs,num_pairs)

		return P, T, C, pair_triangles_orig, pair_inliers, pair_outliers


	def _show_triangle_plots(self, pair_triangles_orig, pair_inliers, pair_outliers):
		component_combinations = pair_triangles_orig.keys()
		NC = len(component_combinations)
		cols, rows = 3, np.ceil(NC/3.0)
		plt.figure(figsize=(15,5*rows))

		for i, combo in enumerate(sorted(component_combinations, key=lambda x: (x[0], x[1]))):
			orig = pair_triangles_orig[combo]
			inliers = pair_inliers[combo]
			outliers = pair_outliers[combo]

			tri_orig_list = []
			for j in range(orig.shape[0]/3):
				tri_orig_list.append(Polygon([Point(*tuple(xy)) for xy in orig[j*3:(j+1)*3,:]]))

			ax = plt.subplot(rows,cols, i+1)
			ax.set_title(combo)

			# Plot triangles
			for t in tri_orig_list:
				plot(t, style="r-", alpha=5.0/self.num_iter, linewidth=1)
			
			# Plot triangle corner points
			for p in orig:
				plt.scatter(p[0],p[1], color="r", alpha=1.0/self.num_iter)

			# Plot datapoints
			plt.scatter(self.X_orig[inliers,combo[0]],self.X_orig[inliers,combo[1]], color="black", alpha=0.8)
			plt.scatter(self.X_orig[outliers,combo[0]],self.X_orig[outliers,combo[1]], color="black", alpha=0.2)



		plt.show()



	def main(self, visualize=False):
		P, T, C, pair_triangles_orig, pair_inliers, pair_outliers = self._build_S(visualize=visualize)
		if visualize:
			self._show_triangle_plots(pair_triangles_orig, pair_inliers, pair_outliers)
		return P, T, C










