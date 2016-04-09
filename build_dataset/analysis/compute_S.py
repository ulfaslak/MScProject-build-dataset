"""Principal Convex Hull Analysis (PCHA) / Archetypal Analysis."""

from __future__ import division
import numpy as np

def compute_S(X, XC, conv_crit=1E-6, maxiter=500):
    """Return S given X and XC (arhcetypes).

    Minimizing ||X - XCS||^2 given X and XC. This script is essentially
    a code snippet from py_PCHA, developed in Matlab by Morten Morup and
    translated to Python by Ulf Aslak.

    Parameters
    ----------
    X : numpy.2darray
        Data matrix in which to find archetypes

    XC : numpy.2darray
        I x noc feature matrix (i.e. XC=X[:,I]*C forming the archetypes)


    Output
    ------
    S : numpy.2darray
        noc x length(U) matrix, S>=0 |S_j|_1=1

    varexlp : float
        Percent variation explained by the model
    """
    def S_update(S, XCtX, CtXtXC, muS, SST, SSE, niter):
        noc, J = S.shape
        e = np.ones((noc, 1))
        for k in range(niter):
            SSE_old = SSE
            g = (np.dot(CtXtXC, S) - XCtX) / (SST / J)
            g = g - e * np.sum(g.A * S.A, axis=0)

            S_old = S
            while True:
                S = (S_old - g * muS).clip(min=0)
                S = S / np.dot(e, np.sum(S, axis=0))
                SSt = S * S.T
                SSE = SST - 2 * np.sum(XCtX.A * S.A) + np.sum(CtXtXC.A * SSt.A)
                if SSE <= SSE_old * (1 + 1e-9):
                    muS = muS * 1.2
                    break
                else:
                    muS = muS / 2

        return S, SSE, muS, SSt
    
    X, XC = X.T, XC.T
    
    noc = XC.shape[1]

    N, M = X.shape

    U = range(M)

    SST = np.sum(X[:, U] * X[:, U])

    muS = 1

    XCtX = np.dot(XC.T, X[:, U])
    CtXtXC = np.dot(XC.T, XC)
    S = -np.log(np.random.random((noc, len(U))))
    S = S / np.dot(np.ones((noc, 1)), np.mat(np.sum(S, axis=0)))
    SSt = np.dot(S, S.T)
    SSE = SST - 2 * np.sum(XCtX.A * S.A) + np.sum(CtXtXC.A * SSt.A)
    S, SSE, muS, SSt = S_update(S, XCtX, CtXtXC, muS, SST, SSE, 25)
    varexpl = (SST - SSE) / SST

    return S.T, varexpl