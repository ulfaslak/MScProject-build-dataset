"""
"""

from sensible_raw.loaders import loader
import pandas as pd
from collections import Counter
from datetime import datetime as dt
import numpy as np
import os

from build_dataset.workers import load_sensible_data as lsd
from build_dataset.workers import apply_time_constraints as atc

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
            self.df_screen.to_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_screen.pickle' % auxlabel)
            
        else:
            # Load
            print "[screen] Loading datasource from local."
            self.df_screen = pd.read_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_screen.pickle' % auxlabel)
            self.users = set(self.df_screen['user'])
        
        print "[screen] Number of datapoints in range:", len(self.df_screen)
        
        
    def __get_user_sessions(self):
        """Return list of sessions (timestamps (start) and durations).
        Currently considers only 1 -> 0 events in the data, even though
        1 -> 1 and 0 -> 0 events do occur (~0.7% of event-pairs). If input
        df is sorted, output is guaranteed to be sorted in the same order,
        because the function loops through rows in original order.

        Parameters
        ----------
        user : int-id

        Returns
        -------
        sessions : list of dicts

            Example
            -------
            >>> __get_user_sessions(0)
            [
                {'timestamp': 51253556, 'duration': 8}, 
                {'timestamp': 51263254, 'duration': 1},
                 ...
            ]
        """
        df = self.df_screen[self.df_screen['user']==self.user].sort(['timestamp'], ascending=[1])
        sessions = []
        i = 0
        for row in df.iterrows():
            event = row[1]['screen_on']
            times = row[1]['timestamp']
            if i == 0:
                prev_event = event
                prev_times = times
                i+=1; continue
            elif event == 0 and prev_event == 1:
                duration = (times-prev_times)/1000
                sessions.append({'timestamp': prev_times/1000, 
                                 'duration': duration})

            #if times == prev_times and event == prev_event:
            #    print i, times, prev_times, event, prev_event

            prev_event = event
            prev_times = times

            i+=1

        return sessions
        
    
    def _compute_summed_usage(self):
        summed_usage = np.sum([i['duration'] for i in self.sessions])
        return {'%s[screen]_summed_usage' % self.auxlabel: summed_usage}
    
    def _compute_session_duration(self):
        """Compute average duration of sessions
            Important to keep in mind here, is that many sessions will have duration 0s.
            This is supposedly because users commonly check their phones for the time, only
            activating it for a very brief moment.
        """
        session_duration = np.mean([i['duration'] for i in self.sessions])
        return {'%s[screen]_session_duration' % self.auxlabel: session_duration}
    
    def _compute_session_count(self):
        """Compute session count.
            This feature measures how much the user generally pulls out his/her phone.
            Counts only 'screen on' events, since they carry most signal for this measurement.
        """
        session_count = len(self.sessions)
        return {'%s[screen]_session_count' % self.auxlabel: session_count}
    
    def _compute_wake_up_time(self):
        """Compute wakeup time.
        Wake up time is assumed to coincide with the first 1-event following the longest 
        break starting no later then 6 am. If the participant takes no break 
        """
        pass
    
    
    def __transform_datapoint(self,datapoint):
        instructions = {
            '%s[screen]_summed_usage' % self.auxlabel: (lambda x: np.log(x)),
            '%s[screen]_session_duration' % self.auxlabel: (lambda x: np.sqrt(x)), 
            '%s[screen]_session_count' % self.auxlabel: (lambda x: np.log(x))}
        
        datapoint = dict((k, instructions[k](v)) for k,v in datapoint.items())
        
        return datapoint
    
    
    def __filtering_condition(self, datapoint, feature, thr):
        if feature in datapoint:
            if datapoint[feature] <= 0:
                raise Exception('[screen] %d %s is 0' % (self.user,feature))
    
    def main(self, user, transformed=True):
        if user not in self.users:
            raise Exception('[screen] User %s not in dataset' % user)
        
        self.user = user
        self.sessions = self.__get_user_sessions()    
        
        datapoint = {}
        
        extractors = [self._compute_summed_usage(),
                      self._compute_session_duration(),
                      self._compute_session_count()]
        
        # Exclusion condition
        for i, ex in enumerate(extractors):
            if i in self.suppress:
                continue
            datapoint.update(ex)
        
        # Add filtering conditions
        self.__filtering_condition(datapoint, '%s[screen]_summed_usage' % self.auxlabel, 0)
        self.__filtering_condition(datapoint, '%s[screen]_session_duration' % self.auxlabel, 0)
        self.__filtering_condition(datapoint, '%s[screen]_session_count' % self.auxlabel, 0)
        
        if transformed:
            datapoint = self.__transform_datapoint(datapoint) 
            
        return datapoint