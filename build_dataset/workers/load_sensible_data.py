from sensible_raw.loaders import loader
from datetime import datetime as dt
import pandas as pd

def load(spans, dataset):
    """Load touched datasets given time constraint.
    
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
            print dataset, "%s_%d" % (m, y)
            columns, data = loader.load_data("sms", "january_2014")
            dict_tmp = {}
            for column, array in zip(columns, data):
                dict_tmp[column] = array
            df = pd.concat([df, pd.DataFrame(dict_tmp)], ignore_index=True)
                
    return df