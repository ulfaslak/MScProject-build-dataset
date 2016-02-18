"""Build T-ratio similarity matrix S

Function run() tak
"""

import subprocess
import numpy as np

def run(X):
	"""Produce trait-similarity matrix S from a trait-space matrix X

	The script takes a matrix, saves it as csv, then launches matlab, loads
	matrix that was just stored and feeds it as input to ComputeSimilarityMat
	which is a matlab function that produces the similarity matrix. The output
	of this function is then again stored as .csv, then loaded using numpy and
	returned by this function.
	"""
	np.savetxt('data/X.csv', X, delimiter=",")

	matlab_code = "cd('matlab');" \
				  "X=csvread('../data/X.csv');" \
				  "S=ComputeSimilarityMat(X,2);" \
				  "csvwrite('../data/S.csv',S);" \
				  "quit;"

	matlab_call = ["matlab", "-nodesktop", "-nosplash", "-r", matlab_code]

	subprocess.call(matlab_call)

	S = np.genfromtxt('data/X.csv', delimiter=",")

	return S