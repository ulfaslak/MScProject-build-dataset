from pareto_clustering.cluster import cluster_Infomap
from pareto_clustering.cluster import cluster_DBSCAN


class Pareto_cluster(object):

    def __init__(self, num_iter=100, sample_size=0.5, remove_outliers=True, visualize=False):
        self.num_iter = num_iter
        self.sample_size = sample_size
        self.remove_outliers = remove_outliers
        self.visualize = visualize

    def fit(self, X, PCHA=False):
        if not PCHA:
            from pareto_clustering.cluster.build_S import Build_S
            self.P, self.T, self.C = Build_S(
                X, self.num_iter, self.sample_size, self.remove_outliers
            ).main(self.visualize)
        else:
            from pareto_clustering.cluster.build_S_PCHA import Build_S
            self.P, self.T, self.C = Build_S(
                X, self.num_iter, self.sample_size, self.remove_outliers
            ).main(self.visualize)

    def Infomap(self):
        self.clusters_infomap, self.indicator_flow = cluster_Infomap.fit(self.T)
        return self.clusters_infomap

    def DBSCAN(self):
        self.clusters_dbscan = cluster_DBSCAN.fit(self.T)
        return self.clusters_dbscan