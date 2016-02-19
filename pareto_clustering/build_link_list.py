import numpy as np

def run(S):
	N, N = S.shape

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
		link_list += '\n%d "%s" 1.0' % ((i+1), f)

	link_list += "\n*Arcs %d" % (N*(N-1)/2)

	for i in range(N):
		for j in range(N):
			if j > i:
				link_list += "\n" + "%d %d %0.2f" % (i+1, j+1, S[i,j])

	with open('link_list.net', 'w') as outfile:
		outfile.write(link_list)

S = np.genfromtxt('data/S.csv', delimiter=",")

run(S)
