import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import polars as pl
import multiprocessing as mp
import json
df1 = pd.read_parquet("../thesis/dataset.parquet")

# Define a function to read a dataset
def read_dataset(file_path):
    df2 = pd.read_parquet(file_path)
    print(file_path, " ::::::::: ", len(df2))
            
    result = pd.merge(df1, df2, right_on='content.source.pdfsha', left_on='id' , how='inner')[["id","fieldOfStudy","year"]]
    
    print("joined len: ", len(result))
    return result
    

def readParquetIds():
    inputFiles = []
    final = pd.DataFrame()
    
    for i in range(30):
        inputFiles.append(str(i) + ".parquet")
        
        res = read_dataset(str(i) + ".parquet")
        final = final.append(res)
    
    final.to_parquet("combinedDS.parquet")
 

if __name__ == '__main__':
    readParquetIds()


