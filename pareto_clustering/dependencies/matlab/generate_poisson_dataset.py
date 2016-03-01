import subprocess
import numpy as np

def generate_poisson_dataset(lambda_, dimensions, num_points, varargin):
    """Run matlab generatePoissonDataset function as subprocess

    Parameters
    ----------
    X : numpy.ndarray

    Returns
    -------
    S : numpy.ndarray
    """
    args = (lambda_, dimensions, num_points, varargin)
    
    # Code executed in Matlab. Important to end with quit;
    matlab_code = [
        "cd('pareto_clustering');",
        "cd('dependencies');",
        "cd('matlab');",
        "output=generatePoissonDataset(%d, %d, %d, %d);" % args,
        "X=output{1,1}; labels=output{1,2};",
        "csvwrite('../data_tmp/X_sim.csv',X);",
        "csvwrite('../data_tmp/labels_sim.csv',labels);",
        "quit;"
        ]

    # -nosplash suppresses the splash window on startup
    matlab_call = ["matlab", "-nodesktop", "-nosplash", "-r", ''.join(matlab_code)]
    subprocess.call(matlab_call)

    # Load the .csv file that Matlab dumps after finishing
    X_sim = np.genfromtxt('pareto_clustering/data_tmp/X_sim.csv', delimiter=",")
    labels_sim = np.genfromtxt('pareto_clustering/data_tmp/labels_sim.csv', delimiter=",")

    return X_sim, labels_sim