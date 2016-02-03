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
            print "... succes! Saving."
            self.df_bluetooth.to_pickle(ROOTPATH + '/data/%sdf_bluetooth.pickle' % auxlabel)
            
        else:
            # Load
            print "[bluetooth] Loading datasource from local."
            self.df_bluetooth = pd.read_pickle(ROOTPATH + '/data/%sdf_bluetooth.pickle' % auxlabel)
            self.users = set(self.df_bluetooth['user'])
        
        print "[bluetooth] Number of datapoints in range:", len(self.df_bluetooth)
        
        
    def __compute_entropy(self, user):
        state_counter = Counter()

        connections = list(self.df_bluetooth[self.df_bluetooth['user'] == user]['bt_mac'])
        state_counter.update(connections)

        p = np.array(state_counter.values()) * 1.0/len(connections)
        
        Ni = len(p); entropy = 0.0
        for j in range(Ni):
            entropy -= p[j]*np.log(p[j])
        return entropy

    
    def main(self, user):
        if user not in self.users:
            raise Exception('User %s not in dataset' % user)
            
        return {'%sbluetooth_social_entropy' % self.auxlabel: self.__compute_entropy(user)}