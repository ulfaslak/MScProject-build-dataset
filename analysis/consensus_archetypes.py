import pandas as pd
import numpy as np

def get_weights(variance=False):
    df_main = pd.read_csv('../data/archetypes.csv')

    df1 = df_main.iloc[:,range(0,5)]
    df2 = df_main.iloc[:,range(5,10)]
    df3 = df_main.iloc[:,range(10,15)]
    df4 = df_main.iloc[:,range(15,20)]

    # Find median, mean and std of each archetype trait
    df_std = np.empty((6,5))
    dfs = [df1, df2, df3, df4]

    for i,_ in enumerate(df_main.iterrows()):
        for j in range(5):
            vals = [df.iloc[i,j] for df in dfs]
            df_std[i,j] = np.std(vals)

    df_std = pd.DataFrame(df_std, columns=['O','C','E','A','N'])
    
    if variance:
        return 1/df_std**2
    else:
        return 1/df_std