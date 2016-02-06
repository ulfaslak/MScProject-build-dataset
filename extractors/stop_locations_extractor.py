from sensible_raw.loaders import loader
import pandas as pd
from collections import Counter
from datetime import datetime as dt
import numpy as np
import os

from workers import load_sensible_data as lsd
from workers import apply_time_constraints as atc

class Stop_locations_extractor:

    def __init__(self, time_constraint, suppress=[], auxlabel="", load_old_datasources=False):
        
        self.suppress = suppress
        self.auxlabel = auxlabel
        
        ROOTPATH = os.path.abspath('')
        
        if not load_old_datasources:
            print "[stop_locations] Building datasource from scratch ...",
        
            df_stop_locations = lsd.load(time_constraint['spans'], "stop_locations")

            df_stop_locations = atc.apply(df_stop_locations, time_constraint)

            # Sort dataframe
            self.df_stop_locations = df_stop_locations.sort(['timestamp'], ascending=[1])
            self.users = set(self.df_stop_locations['user'])
            
            # Save
            print "...succes! Saving."
            self.df_stop_locations.to_pickle(ROOTPATH + '/data_cache/%sdf_stop_locations.pickle' % auxlabel)
            
        else:
            # Load
            print "[stop_locations] Loading datasource from local."
            self.df_stop_locations = pd.read_pickle(ROOTPATH + '/data_cache/%sdf_stop_locations.pickle' % auxlabel)
            self.users = set(self.df_stop_locations['user'])
        
        print "[stop_locations] Number of datapoints in range:", len(self.df_stop_locations)
        
        
    def _compute_entropy(self, user):
        state_counter = Counter()

        states = list(self.df_stop_locations[self.df_stop_locations['user'] == user]['label'])
        state_counter.update(states)

        p = np.array(state_counter.values()) * 1.0/len(states)
        
        Ni = len(p); entropy = 0.0
        for j in range(Ni):
            entropy -= p[j]*np.log(p[j])
        return entropy

    
    def main(self, user):
        if user not in self.users:
            raise Exception('[stop_locations] User %s not in dataset' % user)
            
        datapoint = {'%sstop_locations_geospacial_entropy' % self.auxlabel: self._compute_entropy(user)}
        
        # Add outlier conditions
        if datapoint['%sstop_locations_geospacial_entropy' % self.auxlabel] == 0:
            raise Exception('[stop_locations] %d %sstop_locations_geospacial_entropy is 0' % (user,self.auxlabel))
            
        return datapoint