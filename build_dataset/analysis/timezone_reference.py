import numpy as np
from collections import defaultdict, Counter
from datetime import datetime as dt
import os
import json

from build_dataset.workers import load_sensible_data as lsd


class Load_timezone_reference:
    """Load (or build) timezone_reference
    The point of this module is to create a reference that that maps a timestamp
    to a location.
    
    Parameters
    ----------
    tc : dict
        Specification on which type of period locations should be loaded for.
        
    load_cached : bool
        Specification of whether to build reference from scratch or load existing version
        
    Output
    ------
    out : JSON
        JSON datastructure storing timestamps where location is not same timezone as Denmark.
    """
    
    def __init__(self, tc, load_cached=True):
        self.fileversion = hash(str(tc))%10000000
        
        self.ROOTPATH = os.path.abspath('').split('build_dataset')[0]
        
        if load_cached:
            try:
                self.timezone_reference = self._load()
                self.users = set(self.timezone_reference.keys())
            except IOError:
                load_cached = False

        if not load_cached:
            self.df_location = lsd.load(tc, "location")
            self.users = set(self.df_location['user'])
            self.timezone_reference = self._build_timezone_reference()
            self._save(self.timezone_reference)
            
    def _save(self,data):
        with open(self.ROOTPATH+'build_dataset/data_cache/%dtimezone_reference.json' % self.fileversion, 'w') as outfile:
            json.dump(data, outfile)
            
    def _load(self):
        with open(self.ROOTPATH+'build_dataset/data_cache/%dtimezone_reference.json' % self.fileversion) as infile:
            return json.load(infile)
        
    def __timezone_offset(self, longitude):
        """Compute timeoffset only from longitude"""
        return np.floor((longitude+7.5)/15)-1
        
    def _build_timezone_reference(self):
        ds = dict()
        
        for u in self.users:
            if u % 50 == 0: print u,
            df_u = self.df_location[self.df_location['user']==u].sort(['timestamp'], ascending=1)
            bins, bin_offsets = [], []
            prev_offset = None
            
            for row in df_u.iterrows():
                offset = self.__timezone_offset(row[1]['lon'])
                
                if offset != prev_offset: 
                    bins.append(row[1]['timestamp']/1000)
                    bin_offsets.append(offset)     
                    prev_offset = offset
                    
            ds[str(u)] = {'bins': bins, 'bin_offsets': bin_offsets} 
            
        return ds
    
    def timezone_offset(self, user, timestamp):
        reference_u = self.timezone_reference[str(user)]
        offset_bin = np.digitize(timestamp, reference_u['bins'], right=True) - 1
        return reference_u['bin_offsets'][offset_bin]
            
            
            