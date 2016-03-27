from pareto_clustering.formatting import build_link_list
import subprocess, os
from collections import defaultdict
import re

def fit(T):
    """Run Infomap community detection

    Parameters
    ----------
    T : numpy.ndarray
        Adjacency matrix of T-ratios

    Returns
    -------
    communities : list of lists
    """

    ROOTPATH = os.path.abspath('').split('pipeline_code')[0] + "pipeline_code/"

    # Get network in string format and define filename
    network_string = build_link_list.build_from_T(T, store=False)
    network_filename = 'network.net'
    cluster_filename = 'network.clu'

    # Store locally
    with open(ROOTPATH + "pareto_clustering/data_tmp/" + network_filename, 'w') as outfile:
        outfile.write(network_string)

    # Run Infomap for multiplex network
    subprocess.call([ROOTPATH + 'pareto_clustering/dependencies/Infomap/Infomap',
                     ROOTPATH + 'pareto_clustering/data_tmp/' + network_filename,
                     ROOTPATH + 'pareto_clustering/data_tmp/',
                     '-i',
                     'pajek',
                     '--clu'])

    # Load and parse results
    with open(ROOTPATH + 'pareto_clustering/data_tmp/' + cluster_filename, 'r') as infile:
        network_clusters = infile.read()

    # Get nodes and clusters from .clu file
    no_clu = re.findall(r'\d+ \d+ \d\.\d+', network_clusters)  # ["1 2 0.00800543",...]
    no_clu = sorted([tuple(i.split()) for i in no_clu], key=lambda x: int(x[0]))
    communities_json = defaultdict(list)
    for node, cluster, _ in no_clu:
        communities_json[int(cluster)].append(int(node))

    return communities_json

