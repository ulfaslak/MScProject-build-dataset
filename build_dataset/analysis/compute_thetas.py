import pandas as pd
import numpy as np
from sklearn.preprocessing import scale

def compute_thetas(X, A=None, penalty='consensus', shuffle_arcs=False, return_D=False):
    """Compute N x 6 matrix where columns correspond to BF archetype-wise inverse distance.

    Parameters
    ----------
    X : N x 5 BF-value array

    A : 6 x 5 archetype array

    penalty : str
        Either 'consensus', 'var', 'std', or None. Determines weights to put on distances
        in each BF dimension when measuring inverse weighted euclidian distance.

    shuffle_arcs : bool
        Whether to shuffle arcs or not. Used as 'True' when testing validity of archetypes,
        so default is False.
    """
    def _col_shuf(arr):
        arr = arr.copy()
        for i in range(arr.shape[1]):
            np.random.shuffle(arr[:, i])
        return arr

    def _compute_A():
        A = np.empty((6, 5))
        for i, _ in enumerate(df_main.iterrows()):
            # Loop through columns
            for j in range(5):
                vals = [df.iloc[i, j] for df in dfs]
                A[i, j] = np.median(vals)

        if shuffle_arcs:
            return _col_shuf(A)

        return A

    def _compute_W():
        """Get weight array W."""
        if penalty == "consensus":
            W = 1.0 * np.array(
                [[0, 1, 0, 1, 1],
                 [0, 0, 1, 0, 1],
                 [1, 1, 1, 1, 1],
                 [1, 1, 0, 0, 0],
                 [1, 1, 1, 1, 0],
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

        return W / W.sum(axis=1).reshape((-1, 1))

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
        W = W / W.sum(axis=1).reshape((-1, 1))

    rows, cols = X.shape[0], A.shape[0]
    D = np.zeros((rows, cols))

    for i in range(rows):
        x = X[i, :]
        for j in range(cols):
            a = A[j, :]
            w = W[j, :]
            D[i, j] = _dist(x, a, w)
            
    if return_D:
        return D

    M = np.max(D, axis=1).reshape((-1, 1)) - D
    return M * 1.0 / np.sum(M, axis=1).reshape((-1, 1))
