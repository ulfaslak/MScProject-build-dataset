"""Build T-ratio similarity matrix S

Function run() tak
"""

import subprocess

def run():

	matlab_code = "X=csvread('X.csv');" \
				  "S=ComputeSimilarityMat(X,2);" \
				  "csvwrite('S.csv',S);" \
				  "quit;"

	matlab_call = ["matlab", "-nodesktop", "-nosplash", "-r", matlab_code]

	subprocess.call(matlab_call)