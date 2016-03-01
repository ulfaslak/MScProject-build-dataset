import numpy as np
from collections import defaultdict, Counter
import os
import json

from build_dataset.workers import load_sensible_data as lsd
from build_dataset.workers import apply_time_constraints as atc
from build_dataset.workers import location_is_dorm as lid
from build_dataset.workers import location_is_campus as lic


class Load_location_reference:
    """Load (or build) location_reference
    The point of this module is to create a reference of different locations
    for each user, and their function.
    
    Parameters
    ----------
    time_constraint : dict
        Specification on which type of period locations should be loaded for.
    auxlabel : str
        The label matching time_constraint
    load_reference : bool
        Specification of whether to build reference from scratch or load existing version
        
    Output
    ------
    out : JSON
        JSON datastructure storing each location, with specifications on time features
        as well as type of location (home, campus, fridaybar, 
    """
    
    def __init__(self, time_constraint, auxlabel="", load_reference=True):
        self.auxlabel = auxlabel
        
        self.ROOTPATH = os.path.abspath('')
        
        if not load_reference:
            print "[location_reference] Building datasource from scratch ...",
        
            df_stop_locations = lsd.load(time_constraint['spans'], "stop_locations")
            df_stop_locations = atc.apply(df_stop_locations, time_constraint)

            # Sort dataframe
            self.df_stop_locations = df_stop_locations.sort(["timestamp"], ascending=True)
            self.users = set(self.df_stop_locations['user'])
            
            # Build location reference data structure and save
            self.location_reference = self._build_location_reference()
            self._save_data(self.location_reference)
            
        else:
            # Load
            print "[location_reference] Loading datasource from local."
            with open(self.ROOTPATH + '/build_dataset/data_cache/%slocation_reference.json' % auxlabel) as infile:
                self.location_reference = json.load(infile)
            self.users = set(self.location_reference.keys())
            
            
    def _save_data(self,data):
        # Save
        print "...succes!",
        with open(self.ROOTPATH + '/build_dataset/data_cache/%slocation_reference.json' % self.auxlabel, 'w') as outfile:
            json.dump(data, outfile)
        print "Saved."

        
    def __timezone_offset(self, longitude):
        """Compute timeoffset only from longitude
        """
        return np.floor((longitude+7.5)/15)


    def __compute_states(self, df_u):
        """Compute arrival, duration and coords of events for each location

        Returns
        -------
        states : json

            Example
            -------
            {0: [{'arrival': 1409669100.0,
                  'coordinates': (32.776401774999997, -117.069998025),
                  'duration': 6300.0},
                 {'arrival': 1409697000.0,
                  'coordinates': (32.777439200000003, -117.0703111),
                  'duration': 5400.0},
                  ...],
             1: [{'arrival': 1409669100.0,
                  'coordinates': (32.776401774999997, -117.069998025),
                  'duration': 6300.0},
                 {'arrival': 1409697000.0,
                  'coordinates': (32.777439200000003, -117.0703111),
                  'duration': 5400.0},
                ...
                ],
            ...
            }  
        """
        states = defaultdict(list)
        for row in df_u.iterrows():
            coordina = (row[1]['lat'], row[1]['lon'])
            time_offset = self.__timezone_offset(coordina[1])

            loclabel = row[1]['label']
            arrivalt = row[1]['arrival']+3600*time_offset
            duration = row[1]['delta']

            states[loclabel].append({'arrival': arrivalt, 
                                     'duration': duration, 
                                     'coordinates': coordina})
        return states

    def __bin_24(self, start, duration):
        """Bin seconds in a time-span into to 24 hour buckets.
        """
        # Bin
        bins = [(1+h)*3600 for h in range(24)]
        vals = [x%86400 for x in xrange(int(start),int(start+duration),1)]
        hist = Counter(np.digitize(vals,bins))
        
        # Fill in empty buckets with 0s
        for i in range(24):
            if i not in hist:
                hist[i] = 0
                
        return hist


    def __home_mean_diff(self, time_dist,home_mean=1.5):
        """Compute abs difference between circular mean time
        at given location and mean of circular mean times across
        all locations deemed home (simple criteria and loc=dorm).

        Source of computation for circular mean: 
        http://www.smipple.net/snippet/ptweir/circular%20mean%20and%20variance

        Return
        ------
        out : float
            The circular difference in hours between home_mean and cmean_hour
        """
        to_rad = lambda x: x*2*np.pi/24.0
        to_hou = lambda x: x*24.0/(2*np.pi)
        sinsum = 0
        cossum = 0
        for k,v in time_dist.items():
            sinsum += v*np.sin(to_rad(k))
            cossum += v*np.cos(to_rad(k))
        count = sum(time_dist.values())
        cmean = np.arctan2(sinsum*1.0/count,cossum*1.0/count)
        if cmean < 0: cmean = 2*np.pi + cmean
        cmean_hour = to_hou(cmean)
        if cmean_hour < (12+home_mean):
            return abs(cmean_hour-home_mean)
        else:
            return 24+home_mean - cmean_hour


    def __spread(self, timestamps, timerange):
        """Measures what fraction of days in its span, this location was visited"""
        bins = range(timerange/86400+1)
        vals = (np.array(timestamps)-timestamps[0])/86400
        hist = Counter(np.digitize(vals,bins))

        return len(hist) * 1.0 / len(bins)

    def __type_classifier(self, state_point):
        # Classifiy home location
        if state_point['hmdiff'] < 4:
            if state_point['spread'] > 0.2:
                if state_point['timespent'] > 0.15:
                    if state_point['span'] > 20:
                        return "home"
                    
        # Classify campus location
        if lic.validate(state_point['loca_center']):
            return "campus"
        
        # Classify other
        return "other"


    def _build_location_reference(self):
        ds = dict()
        
        print "\n[location_reference] Building reference from scratch ...",
        for u in self.users:
            # get user stops and summed stops duration
            df_u = self.df_stop_locations[self.df_stop_locations['user'] == u]
            df_u['delta'] = df_u['departure'] - df_u['arrival']
            u_sum_t = sum(df_u['delta'])
            u_t0 = sorted(list(df_u['arrival']))[0]
            u_tt = sorted(list(df_u['departure']))[-1]

            # aggregate state events
            states = self.__compute_states(df_u)

            # compute summary statistics for sttes
            u_states = dict()
            for state, obs_list in states.items():
                #if len(obs_list) == 1: continue
                time_dist = defaultdict(int)
                time_spent = 0
                timestamps_arr = []
                timestamps_dep = []
                loca_dist = []
                for obs in obs_list:
                    # time
                    obs_time_dist = self.__bin_24(obs['arrival'], obs['duration'])
                    for (k,v) in obs_time_dist.items():
                        time_dist[k] += v*1.0/u_sum_t
                    loca_dist.append(obs['coordinates'])
                    timestamps_arr.append(obs['arrival'])
                    timestamps_dep.append(obs['arrival']+obs['duration'])
                    time_spent += obs['duration']

                loca_center = np.mean(zip(*loca_dist),axis=1)
                span_s = max(timestamps_dep)-min(timestamps_arr)

                state_point = {'hmdiff': self.__home_mean_diff(time_dist),
                               'spread': self.__spread(timestamps_arr, int(span_s)),
                               'span': (span_s)/86400,
                               'timespent': time_spent/(span_s),
                               '__dorm': lid.validate(loca_center),
                               'loca_center': tuple(loca_center)}

                state_point['type'] = self.__type_classifier(state_point)

                u_states[state] = state_point

            ds[str(u)] = u_states
            
            if u%5 == 0:
                print u,

        return ds


    def main(self):
        return self.location_reference
