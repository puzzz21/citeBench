import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl
import multiprocessing as mp
import json
df1 = pl.read_parquet("/dataHDD1/pmData/s2orcParsed/len.parquet")
df2 = pl.read_parquet("/dataHDD1/pmData/s2orcParsed/loc.parquet")
df3 = pl.read_parquet("/dataHDD1/pmData/s2orcParsed/type.parquet")

# Define a function to read a dataset
def read_dataset(df1, df2):

    result = df1.join(df2, on='corpusid')
    
    return result
    

def readParquetIds():
    final1 = []
    final2 = []
    final3 = []
    
    for i in range(30):
        df = pl.read_parquet("/dataHDD1/pmData/news2cDownloads/" + str(i) + ".parquet")
         
        print("===================== ")
        print(i)
        res = read_dataset(df1, df)
        final1.append(res)
        res = read_dataset(df2, df)
        final2.append(res)
        res = read_dataset(df3, df)
        final3.append(res)
        
    finalDf1 = pl.concat(final1)
    finalDf1.write_parquet("/dataHDD1/pmData/s2orcParsed/combinedLen.parquet")
    finalDf2 = pl.concat(final2)
    finalDf2.write_parquet("/dataHDD1/pmData/s2orcParsed/combinedLoc.parquet")
    finalDf3 = pl.concat(final3)
    finalDf3.write_parquet("/dataHDD1/pmData/s2orcParsed/combinedType.parquet")
 

if __name__ == '__main__':
    readParquetIds()
