import pandas as pd
import numpy as np

df_main = pd.read_csv('data/archetypes.csv')

df1 = df_main.iloc[:,range(0,5)]
df2 = df_main.iloc[:,range(5,10)]
df3 = df_main.iloc[:,range(10,15)]
df4 = df_main.iloc[:,range(15,20)]
dfs = [df1, df2, df3, df4]

def get_weights(use_variance=True):
    W = np.empty((6,5))

    for i,_ in enumerate(df_main.iterrows()):
        for j in range(5):
            vals = [df.iloc[i,j] for df in dfs]
            W[i,j] = np.std(vals)
    
    if use_variance:
        return 1/W**2
    if use_variance is False:
        return 1/W
    else:
        return W


def get_archetypes(use_mean=False):
    # Find median, mean and std of each archetype trait
    A = np.empty((6,5))

    for i,_ in enumerate(df_main.iterrows()):
        for j in range(5):
            vals = [df.iloc[i,j] for df in dfs]
            if use_mean: A[i,j] = np.mean(vals)
            else: A[i,j] = np.mean(vals)
    
    return A



        