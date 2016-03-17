import pandas as pd
from datetime import datetime as dt
import numpy as np
from build_dataset.analysis import timezone_reference as tzref

def apply(df, time_constraint):
    timezone_offset = tzref.Load_timezone_reference(time_constraint).timezone_offset
    
    df['timestamp'] = df['timestamp']/1000 + np.array(
        [timezone_offset(u, ts)+1 for (u,ts) in zip(df['user'], df['timestamp']/1000)]
    )*3600
    
    return df