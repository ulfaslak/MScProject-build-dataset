import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
from sklearn import svm
from collections import defaultdict

class Outlier_detector:
    """Compute outliers in X matrix
        Performs column-pair-wise topology estimation using one class SVM
        to estimate average topology score pr. datapoint and remove those
        below threshold.
        
    Parameters
    ----------
    X : np.array
        Data matrix of N, M dimensions.
    threshold : float
        Cut off value. Increase to remove more points. 
    visualize : bool
        Instruction whether to visualize detection scheme. Number of output
        figures increases polynomialy with number of columns in X!
        
    Output
    ------
    X_clean : np.array
        Cleaned X matrix.
    """
    
    def __init__(self, X, threshold=-0.5, visualize=False):
        self.X = X
        self.threshold = threshold
        self.visualize = visualize
        self.N, self.M = X.shape
        
        self.component_combinations = []
        for i in range(self.M):
            for j in range(self.M):
                if j > i:
                    self.component_combinations.append((i,j))
                    
        self.clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    
    
    def _compute_outliers(self):
        self.pred_ys = defaultdict(list)

        # Fit the problem for all vector combinations
        for i, combo in enumerate(self.component_combinations):
            # Data generation
            X = self.X[:,combo]

            self.clf.fit(X)
            y_pred = self.clf.decision_function(X).ravel()

            for j,_ in enumerate(y_pred):
                self.pred_ys[j].append(y_pred[j])

        self.pred_avgs = dict((k,np.mean(v)) for k,v in self.pred_ys.items())
        outliers = [k for k,v in self.pred_avgs.items() if v < self.threshold]
    
        return outliers
    
    
    def _show_svm_plots(self):
        outliers = self._compute_outliers()
        for i, combo in enumerate(self.component_combinations):
            # Data generation
            X = self.X[:,combo]
            self.clf.fit(X)
            xx, yy = np.meshgrid(np.linspace(X[:,0].min()-2, X[:,0].max()+2, 500), 
                                 np.linspace(X[:,1].min()-2, X[:,1].max()+2, 500))
                

            plt.figure(figsize=(10, 5))

            # plot the levels lines and the points
            Z = self.clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            
            subplot = plt.subplot(1, 2, 1)
            subplot.set_title(combo)
            subplot.contourf(xx, yy, Z, levels=np.linspace(Z.min(), self.threshold, 7),
                             cmap=plt.cm.Blues_r)
            a = subplot.contour(xx, yy, Z, levels=[self.threshold],
                                linewidths=2, colors='red')
            subplot.contourf(xx, yy, Z, levels=[self.threshold, Z.max()],
                             colors='orange')
            b = subplot.scatter(X[:, 0], X[:, 1], c='white')
            c = subplot.scatter(X[outliers, 0], X[outliers, 1], c='black')
            subplot.axis('tight')
            subplot.legend(
                [a.collections[0], b, c],
                ['learned decision function', 'inliers', 'outliers'],
                prop=matplotlib.font_manager.FontProperties(size=11))
            subplot.set_xlim((X[:,0].min()-2, X[:,0].max()+2))
            subplot.set_ylim((X[:,1].min()-2, X[:,1].max()+2))
        plt.subplots_adjust(0.04, 0.1, 0.96, 0.94, 0.1, 0.26)

        plt.show()
        
        
    def main(self):
        outliers = self._compute_outliers()
        if self.visualize:
            self._show_svm_plots()
        return outliers