from sensible_raw.loaders import loader
import pandas as pd
from collections import Counter
from datetime import datetime as dt
import numpy as np
import os

from workers import load_sensible_data as lsd
from workers import apply_time_constraints as atc

class Bluetooth_extractor:

    def __init__(self, time_constraint, suppress=[], auxlabel="", load_old_datasources=False):
        
        self.suppress = suppress
        self.auxlabel = auxlabel
        
        ROOTPATH = os.path.abspath('')
        
        if not load_old_datasources:
            print "[bluetooth] Building datasource from scratch ...",
        
            df_bluetooth = lsd.load(time_constraint['spans'], "bluetooth_2")

            # Remove non-phone and > 1.5 m connections.
            is_phone = lambda x: (x & 0x001F00) == 0x000200
            df_bluetooth = df_bluetooth[(is_phone(df_bluetooth['class'])==True) & (df_bluetooth['rssi'] > -75)]

            df_bluetooth = atc.apply(df_bluetooth, time_constraint)

            # Sort dataframe
            self.df_bluetooth = df_bluetooth.sort(['timestamp'], ascending=[1])
            self.users = set(self.df_bluetooth['user'])
            
            # Save
            print "...succes! Saving."
            self.df_bluetooth.to_pickle(ROOTPATH + '/data_cache/%sdf_bluetooth.pickle' % auxlabel)
            
        else:
            # Load
            print "[bluetooth] Loading datasource from local."
            self.df_bluetooth = pd.read_pickle(ROOTPATH + '/data_cache/%sdf_bluetooth.pickle' % auxlabel)
            self.users = set(self.df_bluetooth['user'])
        
        print "[bluetooth] Number of datapoints in range:", len(self.df_bluetooth)
        
        
    def _compute_entropy(self):
        state_counter = Counter()

        states = list(self.df_bluetooth[self.df_bluetooth['user'] == self.user]['bt_mac'])
        state_counter.update(states)

        p = np.array(state_counter.values()) * 1.0/len(states)
        
        Ni = len(p); entropy = 0.0
        for j in range(Ni):
            entropy -= p[j]*np.log(p[j])
        
        return {'%s[bluetooth]_social_entropy' % self.auxlabel: entropy}

    
    def __filtering_condition(self, datapoint, feature, thr):
        if feature in datapoint:
            if datapoint[feature] <= 0:
                raise Exception('[bluetooth] %d %s is 0' % (self.user,feature))
    
    def main(self, user):
        if user not in self.users:
            raise Exception('[bluetooth] User %s not in dataset' % user)
            
        self.user = user
            
        datapoint = {}
        
        extractors = [self._compute_entropy()]
        
        # Exclusion condition
        for i, ex in enumerate(extractors):
            if i in self.suppress:
                continue
            datapoint.update(ex)
        
        # Add filtering conditions
        self.__filtering_condition(datapoint,'%s[bluetooth]_social_entropy' % self.auxlabel,0)
            
        return datapoint