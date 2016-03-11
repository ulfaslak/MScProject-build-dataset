from sensible_raw.loaders import loader
from datetime import datetime as dt
import pandas as pd
import numpy as np

def load(tc, dataset):
    def pull(spans, dataset):
        """Pull touched datasets given time constraint.
        
        Parameters
        ----------
        spans : list-of-tuples
            A list of timespans that needs to be loaded data for
        dataset : str
            The name of the dataset that should be loaded
            
        Returns
        -------
        df : Pandas Dataframe
        """
        
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
    
    
    def apply_tc(df, tc):
        """Apply strict time constraints to data"""
        df_tmp = pd.DataFrame()
        for s in tc['spans']:
            df_tmp = pd.concat([
                    df_tmp,
                    df[(df['timestamp']/1000 >= int(dt.strptime(s[0], "%d/%m/%y").strftime("%s"))) & 
                           (df['timestamp']/1000 <= int(dt.strptime(s[1], "%d/%m/%y").strftime("%s")))]
                ])
        df = df_tmp

        # Apply hours and days constraints
        hod = lambda x: np.floor(x%86400/3600)
        dow = lambda x: np.floor((x%(86400*7)/86400+3)%7) #add 3 days cause 0th second is thursday (index 3)

        df = df[(hod(df['timestamp']/1000).isin(tc['hours'])) & 
                (dow(df['timestamp']/1000).isin(tc['days']))]

        return df
    
    
    return apply_tc(
        pull(tc['spans'], dataset),
        tc
    )