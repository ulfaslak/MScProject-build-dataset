import pandas as pd
import numpy as np
from sklearn.preprocessing import scale

class Consensus_archetypes:
    """For big five data, compute consensus archetype matching matrix
    """

    def __init__(self, use_variance=True, use_median=True):
        
        self.use_variance = use_variance
        self.use_median = use_median

        self.df_main = pd.read_csv('data/archetypes.csv')

        df1 = self.df_main.iloc[:,range(0,5)]
        df2 = self.df_main.iloc[:,range(5,10)]
        df3 = self.df_main.iloc[:,range(10,15)]
        df4 = self.df_main.iloc[:,range(15,20)]
        self.dfs = [df1, df2, df3, df4]


    def _get_weights(self, use_variance):
        """Get consensus weights of each archetype trait

        Consensus weights are computed as inverse var or std, of archetype
        traits across the four big five datasets in consideration (Facebook,
        SAPA, MIDUS, SenDTU)

        Parameters
        ----------
        use_variance : bool/other
            Instruction whether to use inverse variance (default) or inverse
            standard deviation as consensus weights. If anything other than a
            bool is specified, the raw standard deviation of the archetype tra-
            its are returned. This should only be used for inspection purposes.

        Output
        ------

        """
        W = np.empty((6,5))

        for i,_ in enumerate(self.df_main.iterrows()):
            for j in range(5):
                vals = [df.iloc[i,j] for df in self.dfs]
                W[i,j] = np.std(vals)

        if use_variance:
            return 1/W**2
        if use_variance is False:
            return 1/W
        else:
            print "Warning: Returning raw std values. Won't work as weights."
            return W


    def _get_archetypes(self, use_median):
        """Compute mean or median values of archetypes across datasets

        Archetypes are computes as mean or median values of archetype traits
        across datasets in consideration (Facebook, SAPA, MIDUS, SenDTU).

        Parameters
        ----------
        use_median : bool
            Specification on whether to compute archetypes using median
            (default) or mean of archetype trait values in datasets.
        """
        A = np.empty((6,5))

        # Loop through rows
        for i,_ in enumerate(self.df_main.iterrows()):
            # Loop through columns
            for j in range(5):
                vals = [df.iloc[i,j] for df in self.dfs]
                if use_median: A[i,j] = np.median(vals)
                else: A[i,j] = np.mean(vals)

        return A


    def __dist(self,y,a,w):
        """Compute the WED between vector y from Y and vector a from A.
        """
        m_ya = 0
        for k in range(5):
            m_ya += (y[k] - a[k])**2 * w[k]
        
        return m_ya


    def project_to_archetype_space(self, Y):
        W = self._get_weights(self.use_variance); W = W/np.mat(W.sum(axis=1)).T
        A = self._get_archetypes(self.use_median)

        rows, cols = Y.shape[0], A.shape[0]

        M = np.empty((rows,cols))

        for i in range(rows):
            y = Y[i,:]
            for j in range(cols):
                a = A[j,:]
                w = W[j,:].A[0]
                M[i,j] = self.__dist(y,a,w)

        return -scale(M)



