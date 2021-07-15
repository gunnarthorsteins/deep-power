import numpy as np
import pandas as pd

df = pd.read_csv("Ln.csv", sep="\t")
df = df.drop(columns='boolean')
df.dags = df.dags.astype("datetime64[ns]")
df = df.replace(-1, 0)

def change_minute(row):
    return row.dags.replace(minute=0)

df.dags = df.apply(lambda r: change_minute(r), axis=1)

for i, j in df.iterrows():
    if df.dags[j] == x:
        df.dags
        k += 1
    k = 0
dff = pd.DataFrame(np.zeros_like(df),
                   index=df.index,
                   columns=df.columns)


# ind = 0
# for i in df:
#     if df.dags.dt.year[i] == df.dags.dt.year[i-1]:
#         if df.dags.dt.month[i] == df.dags.dt.month[i-1]:
#             if df.dags.dt.day[i] == df.dags.dt.day[i-1]:
#                 if df.dags.dt.hour[i] == df.dags.dt.hour[i]:
#                     dff[i] == 
#         df.append()
# val = df.dags.dt.day
# print(val)
