"""
"""

from sensible_raw.loaders import loader
import pandas as pd
from collections import Counter
from datetime import datetime as dt
import numpy as np
import os

from workers import load_sensible_data as lsd
from workers import apply_time_constraints as atc

class Screen_extractor:
    
    def __init__(self, time_constraint, suppress=[], auxlabel="", load_old_datasources=False):
        
        self.suppress = suppress
        self.auxlabel = auxlabel
        
        ROOTPATH = os.path.abspath('')
        
        if not load_old_datasources:
            print "[screen] Building datasource from scratch ...",
        
            df_screen = lsd.load(time_constraint['spans'], "screen")

            df_screen = atc.apply(df_screen, time_constraint)

            # Sort dataframe
            self.df_screen = df_screen.sort(['timestamp'], ascending=[1])
            self.users = set(self.df_screen['user'])
            
            # Save
            print "...succes! Saving."
            self.df_screen.to_pickle(ROOTPATH + '/data_cache/%sdf_screen.pickle' % auxlabel)
            
        else:
            # Load
            print "[screen] Loading datasource from local."
            self.df_screen = pd.read_pickle(ROOTPATH + '/data_cache/%sdf_screen.pickle' % auxlabel)
            self.users = set(self.df_screen['user'])
        
        print "[screen] Number of datapoints in range:", len(self.df_screen)
        
    
    def _compute_summed_usage(user):
        pass
    
    def _compute_session_duration(user):
        """Compute average duration of sessions
            Important to keep in mind here, is that many sessions will have duration 0s.
            This is supposedly because users commonly check their phones for the time, only
            activating it for a very brief moment.
        """
        pass
    
    def _compute_session_count(user):
        """Compute session count.
            This feature measures how much the user generally pulls out his/her phone.
            Counts only 'screen on' events, since they carry most signal for this measurement.
        """
        pass
    
    def _compute_wake_up_time(user):
        pass
    
    
    def main(self, user):
        if user not in self.users:
            raise Exception('[screen] User %s not in dataset' % user)
            
        datapoint = {'%sscreen_summed_usage' % self.auxlabel: self._compute_summed_usage(user),
                     '%sscreen_session_duration' % self.auxlabel: self._compute_session_duration(user), 
                     '%sscreen_session_frequency' % self.auxlabel: self._compute_session_count(user), 
                     '%sscreen_wake_up_time' % self.auxlabel: self._compute_wake_up_time(user)}
        
        # Add outlier conditions
        if datapoint['%sscreen_summed_usage' % self.auxlabel] == 0:
            raise Exception('[screen] %d %sscreen_summed_usage is 0' % (user,self.auxlabel))
        if datapoint['%sscreen_session_duration' % self.auxlabel] == 0:
            raise Exception('[screen] %d %sscreen_session_duration is 0' % (user,self.auxlabel))
        if datapoint['%sscreen_session_frequency' % self.auxlabel] == 0:
            raise Exception('[screen] %d %sscreen_session_frequency is 0' % (user,self.auxlabel))
            
        return datapoint