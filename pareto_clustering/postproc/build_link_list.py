import numpy as np

# if __name__ == '__main__':
# 	from os.path import abspath, dirname; import os
# 	PARENTDIR = abspath("../")
# 	os.sys.path.insert(0, PARENTDIR)

def build_from_P(P):
	N, N = P.shape

	features = ["bluetooth_social_entropy",
				"screen_session_duration",
				"screen_session_frequency",
				"screen_summed_usage",
				"sms_fractions_of_conversations_started",
				"sms_overall_received_responsiveness",
				"sms_overall_responsiveness",
				"sms_selectivity_in_responsiveness",
				"sms_traffic",
				"stop_locations_geospacial_entropy"]

	link_list = "*Vertices %d" % N

	for i, f in enumerate(features):
		link_list += '\n%d "%s" 1.0' % ((i), f)

	link_list += "\n*Arcs %d" % (N*(N-1)/2)

	for i in range(N):
		for j in range(N):
			if j <= i: continue
			if P[i,j] >= 0.5: continue
			weight = -np.log2(P[i,j]+0.01) - 1.01
			link_list += "\n" + "%d %d %0.2f" % (i, j, weight)

	print "Writing file 'link_listP.net'"
	with open('pareto_clustering/data/link_listP.net', 'w') as outfile:
		outfile.write(link_list)


def build_from_T(T):
	N, N = T.shape

	features = ["bluetooth_social_entropy",
				"screen_session_duration",
				"screen_session_frequency",
				"screen_summed_usage",
				"sms_fractions_of_conversations_started",
				"sms_overall_received_responsiveness",
				"sms_overall_responsiveness",
				"sms_selectivity_in_responsiveness",
				"sms_traffic",
				"stop_locations_geospacial_entropy"]

	link_list = "*Vertices %d" % N

	for i, f in enumerate(features):
		link_list += '\n%d "%s" 1.0' % ((i), f)

	link_list += "\n*Arcs %d" % (N*(N-1)/2)

	for i in range(N):
		for j in range(N):
			if j <= i: continue
			if T[i,j] <= 1: continue
			weight = T[i,j] - 1
			link_list += "\n" + "%d %d %0.2f" % (i, j, weight)

	print "Writing file 'link_listT.net'"
	with open('pareto_clustering/data/link_listT.net', 'w') as outfile:
		outfile.write(link_list)


#P = np.loadtxt("../data/P_clean.csv", delimiter=",")
#T = np.loadtxt("../data/T_clean.csv", delimiter=",")

#build_from_P(P)