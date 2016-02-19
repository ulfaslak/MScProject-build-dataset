"""Build T-ratio similarity matrix S

Function run() tak
"""

import subprocess
import numpy as np

def run(X, maxSize=2):
	"""Produce trait-similarity matrix S from a trait-space matrix X

	The script takes a matrix, saves it as csv, then launches matlab, loads
	matrix that was just stored and feeds it as input to ComputeSimilarityMat
	which is a matlab function that produces the similarity matrix. The output
	of this function is then again stored as .csv, then loaded using numpy and
	returned by this function.

	Parameters
	----------
	X : numpy array
	maxSize : int
		Maximum size of trait-subsets for which T-ratio is computes.

	Returns
	-------
	S : numpy array
		Values are proportional to degree of pareto-front sharing
	"""
	np.savetxt('data/X.csv', X, delimiter=",")

	matlab_code = [
	"cd('matlab');", 
	"X=csvread('../data/X.csv');", 
	"S=ComputeSimilarityMat(X,%d);" % maxSize,
	"csvwrite('../data/S.csv',S);",
	"quit;"
	]

	matlab_call = ["matlab", "-nodesktop", "-nosplash", "-r", ''.join(matlab_code)]

	subprocess.call(matlab_call)

	S = np.genfromtxt('data/S.csv', delimiter=",")

	return S

X = np.genfromtxt('../build_dataset/data/X.csv', delimiter=",")
run(X, 3)