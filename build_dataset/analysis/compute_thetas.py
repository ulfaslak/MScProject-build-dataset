import pandas as pd
import numpy as np
from sklearn.preprocessing import scale

def compute_thetas(X, A=None, penalty='consensus'):

    def _compute_A():
        A = np.empty((6, 5))
        for i, _ in enumerate(df_main.iterrows()):
            # Loop through columns
            for j in range(5):
                vals = [df.iloc[i, j] for df in dfs]
                A[i, j] = np.median(vals)
        return np.mat(A)

    def _compute_W():
        """Get weight matrix W."""
        if penalty == "consensus":
            W = np.array(
                [[0, 1, 0, 1, 1],
                 [0, 0, 1, 1, 1],
                 [1, 1, 1, 1, 1],
                 [1, 1, 0, 1, 1],
                 [1, 1, 1, 1, 1],
                 [0, 0, 1, 0, 0]]
            )

        elif penalty in ['var', 'std']:
            W = np.empty((6, 5))
            for i, _ in enumerate(df_main.iterrows()):
                for j in range(5):
                    vals = [df.iloc[i, j] for df in dfs]
                    W[i, j] = np.std(vals)

            if penalty == 'var':
                W = W ** 2
            W = 1 / W
        
        else:
            W = np.ones((6, 5))

        return W / np.mat(W.sum(axis=1)).T

    def _dist(x, a, w):
        """Compute the WED between vector x from X and vector a from A.
        """
        m_xa = 0
        for k in range(len(x)):
            m_xa += (x[k] - a[k])**2 * w[k]

        return m_xa



    if A is None:  # Then build A from Big Five data
        if X.shape[1] != 5:
            raise TypeError('Datapoints needs to have 5 columns.')

        print "Computing Thetas from precomputed archetypes."
        df_main = pd.read_csv('build_dataset/data/archetypes.csv')

        dfs = [
            df_main.iloc[:, range(0, 5)],
            df_main.iloc[:, range(5, 10)],
            df_main.iloc[:, range(10, 15)]
        ]

        A = _compute_A()
        W = _compute_W()

    elif X.shape[1] != A.shape[1]:
        raise TypeError('Datapoints and archetypes have different dimensions.')
    else:
        W = np.ones(A.shape)
        W = W / np.mat(W.sum(axis=1)).T



    rows, cols = X.shape[0], A.shape[0]
    M = np.zeros((rows, cols))
    
    for i in range(rows):
        x = X[i, :]
        for j in range(cols):
            a = A[j, :].A[0]
            w = W[j, :].A[0]
            M[i, j] = _dist(x, a, w)            

    return M