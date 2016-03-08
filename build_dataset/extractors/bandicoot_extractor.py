import bandicoot as bc
import numpy as np
import pandas as pd
from datetime import datetime as dt
import os
from build_dataset.workers import load_sensible_data as lsd
from build_dataset.workers import apply_time_constraints as atc

class Bandicoot_extractor:
    
    def __init__(self, time_constraint, supress=[], auxlabel="", load_old_datasources=False):
        
        self.suppress = suppress
        self.auxlabel = auxlabel
        
        ROOTPATH = os.path.abspath('')
        
        if not load_old_datasources:
            
            print "[bandicoot] Building datasource from scratch ..."
            
            # Load data
            df_call = lsd.load(tc0['spans'], "calllog")
            df_call = atc.apply(df_call, tc0)
            df_sms = lsd.load(tc0['spans'], "sms")
            df_sms = atc.apply(df_sms, tc0)

            # Format call df
            df_call['interaction'] = "call"
            df_call['timestamp'] = [dt.fromtimestamp(t) for t in df_call['timestamp']/1000]
            df_call['type'] = ["in" if t == 1 else "out" for t in df_call['type']]
            df_call.columns = ["call_duration", "correspondent_id", "datetime", "direction", "interaction", "user"]

            # Format sms df
            df_sms = df_sms[df_sms['status'] <= 0]
            df_sms = df_sms[df_sms['type'] <= 2]
            df_sms = df_sms.drop('status', 1)
            df_sms['interaction'] = "text"
            df_sms['timestamp'] = [dt.fromtimestamp(t) for t in df_sms['timestamp']/1000]
            df_sms['type'] = ["in" if t == 1 else "out" for t in df_sms['type']]
            df_sms['call_duration'] = ""
            df_sms.columns = ["correspondent_id", "datetime", "direction", "interaction", "call_duration", "user"]

            # Concatenate
            df = pd.concat([df_sms, df_call])
            
            # Store record for each user
            users = set(list(df_sms['user'])) & set(list(df_call['user']))
            for u in users:
                df_u = df[df['user'] == u]
                df_u = df_u.drop('user', 1).sort(['datetime'], ascending=1)
                df_u.to_csv(ROOTPATH + "/build_dataset/data_cache/records/%d.csv" % u, index=False)
                
        else:
            print "[bandicoot] Loading datasource from local."
            self.users = [int(f.split(".")[0]) for f in os.listdir(ROOTPATH + "/build_dataset/data_cache/records")]
            
            
    def main(self, user):
        record = bc.read_csv(str(user), "records/")
        
        indicators = bc.utils.all(B)
        
        exclude_indicators = ['name', 'reporting', 'number_of_antennas', 'entropy_of_antennas', 
                              'frequent_antennas', 'churn_rate', 'radius_of_gyration', 'percent_at_home']
        
        for ex in exclude_indicators:
            del indicators[ex]
            
        
        
        