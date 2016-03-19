from sensible_raw.loaders import loader
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os


def load(tc, dataset, load_cached=True, filtering=False, offset=True):
    """Load dataset in a given time frame.
    
    This function takes a time frame and a datatype, pulls all affected months
    from the API, transforms the timestamps to respect the user location, and
    finally trims the dataset to meet the requirements specified in argument 'tc'.
        
    Parameters
    ----------
    spans : list-of-tuples
        A list of timespans that needs to be loaded data for.
        
    dataset : str
        The name of the datatype to load.

    Returns
    -------
    df : Pandas Dataframe
    """
    ROOTPATH = os.path.abspath('').split('build_dataset')[0]
    if ROOTPATH[-1] != "/": ROOTPATH += "/"
    
    def _filter_bt_special(df):
        is_phone = lambda x: (x & 0x001F00) == 0x000200
        return df[(is_phone(df['class'])==True) & (df['rssi'] > -75)]
    
    def _load():
        fileversion = hash(str(tc))%10000000
        return pd.read_pickle(ROOTPATH+'build_dataset/data_cache/%d%s.pickle' % (fileversion,dataset))
        
    def _save():
        fileversion = hash(str(tc))%10000000
        df.to_pickle(ROOTPATH+'build_dataset/data_cache/%d%s.pickle' % (fileversion,dataset))
    
    def pull(spans, dataset):
        """Pull touched datasets given time constraint."""
        
        months_int = set(
            [item for sublist in 
             [
                    range(
                        dt.strptime(s[0], "%d/%m/%y").month-1, 
                        dt.strptime(s[1], "%d/%m/%y").month) 
                    for s in spans
                ] 
             for item in sublist])

        months = [dt.strptime(str(m+1), '%m').strftime("%B").lower() for m 
                  in months_int]

        years      = set(
            [item for sublist in 
             [
                    range(
                        dt.strptime(s[0], "%d/%m/%y").year, 
                        dt.strptime(s[1], "%d/%m/%y").year+1) 
                    for s in spans
                ] 
             for item in sublist])

        df = pd.DataFrame()

        for y in years:
            print "<" + str(y) + ">",
            for m in months:
                print m[:3],
                columns, data = loader.load_data(dataset, "%s_%d" % (m, y))
                dict_tmp = {}
                for column, array in zip(columns, data):
                    dict_tmp[column] = array
                df = pd.concat([df, pd.DataFrame(dict_tmp)], ignore_index=True)
                    
        return df

    def correct_offset(df, time_constraint):
        """Correct timestamps with respects to location."""
        from build_dataset.analysis import timezone_reference as tzref
        timezone_offset = tzref.Load_timezone_reference(time_constraint).timezone_offset

        df['timestamp'] = df['timestamp']/1000 + np.array(
            [timezone_offset(u, ts)+1 for (u,ts) in zip(df['user'], df['timestamp']/1000)]
            )*3600
        
        if dataset == "stop_locations":
            df['arrival'] += np.array(
                [timezone_offset(u, ts)+1 for (u,ts) in zip(df['user'], df['arrival'])]
            )*3600
            df['departure'] += np.array(
                [timezone_offset(u, ts)+1 for (u,ts) in zip(df['user'], df['departure'])]
            )*3600

        return df
    
    def apply_tc(df, tc):
        """Apply strict time constraints to data."""
        df_tmp = pd.DataFrame()
        for s in tc['spans']:
            df_tmp = pd.concat([
                    df_tmp,
                    df[(df['timestamp'] >= int(dt.strptime(s[0], "%d/%m/%y").strftime("%s"))) & 
                           (df['timestamp'] <= int(dt.strptime(s[1], "%d/%m/%y").strftime("%s")))]
                ])
        df = df_tmp

        # Apply hours and days constraints
        hod = lambda x: np.floor(x%86400/3600)
        dow = lambda x: np.floor((x%(86400*7)/86400+3)%7) #add 3 days bc 0th second is thursday (index 3)

        df = df[(hod(df['timestamp']/1000).isin(tc['hours'])) & 
                (dow(df['timestamp']/1000).isin(tc['days']))]

        return df
    
    
    if load_cached:
        try: 
            return _load()
        except IOError:
            pass
    
    df = pull(tc['spans'], dataset)                        # Pull raw data
    if offset: df = correct_offset(df, tc)                 # Location offset
    df = apply_tc(df, tc).sort(['timestamp'], ascending=1) # Strict time constraint
    
    if filtering == "bt_special":
        df = _filter_bt_special(df)
        
    _save()
    
    return df