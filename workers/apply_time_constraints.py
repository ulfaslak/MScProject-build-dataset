import pandas as pd
from datetime import datetime as dt
import numpy as np

def apply(df, time_constraint):
    df_tmp = pd.DataFrame()
    for s in time_constraint['spans']:
        df_tmp = pd.concat([
                df_tmp,
                df[(df['timestamp']/1000 >= int(dt.strptime(s[0], "%d/%m/%y").strftime("%s"))) & 
                       (df['timestamp']/1000 <= int(dt.strptime(s[1], "%d/%m/%y").strftime("%s")))]
            ])
    df = df_tmp

    # Apply hours and days constraints
    hod = lambda x: np.floor(x%86400/3600)
    dow = lambda x: np.floor((x%(86400*7)/86400+3)%7) #add 3 days cause 0th second is thursday (index 3)

    df = df[(hod(df['timestamp']/1000).isin(time_constraint['hours'])) & 
            (dow(df['timestamp']/1000).isin(time_constraint['days']))]

    return df