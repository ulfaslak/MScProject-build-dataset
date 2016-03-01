from sensible_raw.loaders import loader
import pandas as pd
from collections import Counter
from datetime import datetime as dt
import numpy as np
import os

from build_dataset.workers import load_sensible_data as lsd
from build_dataset.workers import apply_time_constraints as atc

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
            self.df_stop_locations.to_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_stop_locations.pickle' % auxlabel)
            
        else:
            # Load
            print "[stop_locations] Loading datasource from local."
            self.df_stop_locations = pd.read_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_stop_locations.pickle' % auxlabel)
            self.users = set(self.df_stop_locations['user'])
        
        print "[stop_locations] Number of datapoints in range:", len(self.df_stop_locations)
        
        
    def _compute_entropy(self):
        state_counter = Counter()

        states = list(self.df_stop_locations[self.df_stop_locations['user'] == self.user]['label'])
        state_counter.update(states)

        p = np.array(state_counter.values()) * 1.0/len(states)
        
        Ni = len(p); entropy = 0.0
        for j in range(Ni):
            entropy -= p[j]*np.log(p[j])
        
        return {'%s[stop_locations]_geospacial_entropy' % self.auxlabel: entropy}
    
    
    def __filtering_condition(self, datapoint, feature, thr):
        if feature in datapoint:
            if datapoint[feature] <= 0:
                raise Exception('[stop_locations] %d %s is 0' % (self.user,feature))

    
    def main(self, user):
        if user not in self.users:
            raise Exception('[stop_locations] User %s not in dataset' % user)
            
        self.user = user
            
        datapoint = {}
        
        extractors = [self._compute_entropy()]
        
        # Exclusion condition
        for i, ex in enumerate(extractors):
            if i in self.suppress:
                continue
            datapoint.update(ex)
        
        # Add filtering conditions
        self.__filtering_condition(datapoint, '%s[stop_locations]_geospacial_entropy' % self.auxlabel, 0)
            
        return datapoint