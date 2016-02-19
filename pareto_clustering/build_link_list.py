import numpy as np

def run(S):
	N, N = S.shape

	link_list = "#source target weight."

	for i in range(N):
		for j in range(N):
			if j > i:
				link_list += "\n" + "%d %d %0.2f" % (i+1, j+1, S[i,j])

	with open('link_list.txt', 'w') as outfile:
		outfile.write(link_list)

S = np.genfromtxt('data/S.csv', delimiter=",")

run(S)
