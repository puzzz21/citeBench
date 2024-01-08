import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl
import multiprocessing as mp
import json

def readParquetIds():
    final = []
    
    
    for i in range(30):
        df = pl.scan_parquet("/dataHDD1/pmData/news2cDownloads/" + str(i) + ".parquet").select(["corpusid"]).collect()
        print(df)
        final.append(df)
        
    finalDf = pl.concat(final)
    
    finalDf.write_parquet("/dataHDD1/pmData/news2cDownloads/combinedDSIds.parquet")
 

if __name__ == '__main__':
    readParquetIds()


