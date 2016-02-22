from point_location import min_triangle as mint
from point_location.geo.shapes import Point, Polygon
from point_location.geo.spatial import toNumpy
from point_location.geo.drawer import plot
import numpy as np
import signal
import matplotlib.pylab as plt
from matplotlib.patches import Ellipse

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

class Build_S:
    """Build Similarity matrices
    
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
    	geometry modeling with low sensitibity to outliers (low).
        
    Returns
    -------
    P : numpy.ndarray
        M x M matrix of trait-pair triangle-p-values
    T : numpy.ndarray
        M x M matrix of trait-pair triangle-T-ratios
    C : numpy.ndarray
        M x M matrix of trait-pair triangle success bootstrapping iterations
    """

    def __init__(self, X, num_iter=100,sample_size=0.5):
    	self.X_orig = X
    	self.N, self.M = X.shape
        self.num_iter = num_iter
        self.sample_size = sample_size

        self.subsets = []
        for n in range(num_iter):
            self.subsets.append(np.random.randint(0,self.N,size=int(self.N*sample_size)))
            
        # Change the behavior of SIGALRM
        signal.signal(signal.SIGALRM, timeout_handler)


    def __get_area(self, X):
        while True:
            points = [Point(*tuple(p)) for p in X]
            min_tri = mint.minTriangle(Polygon(points))
            area = min_tri.area()

            # To correct for occational faulty "super small" area computed.
            # In effect calling continue on the loop will cause the operation
            # to timeout, and the subset to be skipped in bootstrapping.
            if area < 0.001: continue

            break

        return points, min_tri, area


    def _build_S(self, visualize):
        P = np.zeros((self.M, self.M))
        T = np.zeros((self.M, self.M))
        C = np.zeros((self.M, self.M))
        STD_orig = np.zeros((self.M, self.M))
        STD_shuf = np.zeros((self.M, self.M))

        compute_area = lambda P: abs((P[0]*(P[3]-P[5]) + P[2]*(P[5]-P[1]) + P[4]*(P[1]-P[3])) / 2.0)

    	pair_triangles_orig = {}
    	pair_triangles_shuf = {}

        for i in range(self.M):
            print i, "vs...",
            for j in range(self.M):
                if j <= i: continue

                Xpair_orig = self.X_orig[:,[i,j]]
                Xpair_shuf = Xpair_orig.copy()
                for k in range(2):
                	np.random.shuffle(Xpair_shuf[:,k])

                areas_s_orig = []
                areas_s_shuf = []

                tri_points_s_orig = np.empty((6,self.num_iter))
                tri_points_s_shuf = np.empty((6,self.num_iter))

                # Bootstrapping
                t = 0
                loop_over = range(self.num_iter)
                for n in loop_over:
                    #subset_indices = np.array(list(set(self.subsets[n])))
                    subset_indices = np.random.randint(0,self.N,size=int(self.N*self.sample_size))

                    Xpair_s_orig = Xpair_orig[subset_indices,:]
                    Xpair_s_shuf = Xpair_shuf[subset_indices,:]

                    signal.setitimer(signal.ITIMER_REAL,0.02)
                    try:
                        points_s_orig, min_tri_s_orig, tri_s_area_orig = self.__get_area(Xpair_s_orig)
                        points_s_shuf, min_tri_s_shuf, tri_s_area_shuf = self.__get_area(Xpair_s_shuf)
                        signal.setitimer(signal.ITIMER_REAL,0)
                    except ValueError: 
                    	t+=1
                    	#if len(self.subsets) < self.num_iter+t:
                    		#self.subsets.append(np.random.randint(0,self.N,size=int(self.N*self.sample_size)))
                    	signal.setitimer(signal.ITIMER_REAL,0)
                    	loop_over.append(self.num_iter-1+t)
                    	continue
                    except TimeoutException: 
                    	t+=1
                    	#if len(self.subsets) < self.num_iter+t:
                    		#self.subsets.append(np.random.randint(0,self.N,size=int(self.N*self.sample_size)))
                    	loop_over.append(self.num_iter-1+t)
                    	continue
                    else: 
                    	signal.setitimer(signal.ITIMER_REAL,0)

                    areas_s_orig.append(tri_s_area_orig)
                    areas_s_shuf.append(tri_s_area_shuf)
                    tri_points_s_orig[:,n-t] = toNumpy(min_tri_s_orig.points).reshape((6,1)).T
                    tri_points_s_shuf[:,n-t] = toNumpy(min_tri_s_shuf.points).reshape((6,1)).T

                P[i,j] = np.mean(np.array(areas_s_orig) >= np.array(areas_s_shuf))
                T[i,j] = compute_area(np.mean(tri_points_s_shuf,axis=1)) / compute_area(np.mean(tri_points_s_orig,axis=1))
                C[i,j] = len(areas_s_shuf)
                STD_orig[i,j] = np.mean(np.std(tri_points_s_orig,axis=1))
                STD_shuf[i,j] = np.mean(np.std(tri_points_s_shuf,axis=1))

                if visualize:
                	# pair_triangles_orig[(i,j)] = {'mean': np.median(tri_points_s_orig,axis=1), 'std': np.std(tri_points_s_orig,axis=1)}
                	# pair_triangles_shuf[(i,j)] = {'mean': np.median(tri_points_s_shuf,axis=1), 'std': np.std(tri_points_s_shuf,axis=1)}
                	pair_triangles_orig[(i,j)] = tri_points_s_orig.T.reshape(-1,2)
                	pair_triangles_shuf[(i,j)] = tri_points_s_shuf.T.reshape(-1,2)
                print "\t%d(%d)" % (j,t),
            print

        return P, T, C, STD_orig, STD_shuf, pair_triangles_orig, pair_triangles_shuf


    def _show_triangle_plots(self, pair_triangles_orig, pair_triangles_shuf):
    	component_combinations = pair_triangles_orig.keys()
    	NC = len(component_combinations)
    	cols, rows = 3, np.ceil(NC/3.0)
        plt.figure(figsize=(15,5*rows))

        for i, combo in enumerate(sorted(component_combinations, key=lambda x: (x[0], x[1]))):
        	orig = pair_triangles_orig[combo]
        	shuf = pair_triangles_shuf[combo]

        	tri_orig_list = []
        	tri_shuf_list = []
        	for j in range(orig.shape[0]/3):
        		tri_orig_list.append(Polygon([Point(*tuple(xy)) for xy in orig[j*3:(j+1)*3,:]]))
        		tri_shuf_list.append(Polygon([Point(*tuple(xy)) for xy in shuf[j*3:(j+1)*3,:]]))

        	# eli_orig = [Ellipse(xy=m, width=s[0], height=s[1]) for m, s in zip(orig['mean'].reshape(3,2),orig['std'].reshape(3,2))]
        	# eli_shuf = [Ellipse(xy=m, width=s[0], height=s[1]) for m, s in zip(shuf['mean'].reshape(3,2),shuf['std'].reshape(3,2))]

        	ax = plt.subplot(rows,cols, i+1)
        	ax.set_title(combo)
        	# for e in range(3):
        	# 	ax.add_artist(eli_orig[e])
        	# 	eli_orig[e].set_alpha(0.3)
        	for t in tri_orig_list:
        		plot(t, style="r-", alpha=0.1, linewidth=1)
        	for p in orig:
        		plt.scatter(p[0],p[1], color="r", alpha=0.1)
        	plt.scatter(self.X_orig[:,combo[0]],self.X_orig[:,combo[1]])

        plt.show()



    def main(self, visualize=False):
        P, T, C, STD_orig, STD_shuf, pair_triangles_orig, pair_triangles_shuf = self._build_S(visualize=visualize)
        if visualize:
        	self._show_triangle_plots(pair_triangles_orig,pair_triangles_shuf)
        return P, T, C, STD_orig, STD_shuf, pair_triangles_orig, pair_triangles_shuf










