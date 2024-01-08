from datasets import load_dataset
import pandas as pd
import psutil
from functools import cache
import time

@cache
def load_data():
    start_time = time.time()

    
    df = pd.read_parquet("dataset.parquet")
    print(df)
    
    fields = ['Computer Science','Medicine','Art','Materials Science','Engineering','Chemistry','Physics','Biology','History',
              'Geography','Psychology','Business','Geology','Economics','Political Science','Environmental Science','Philosophy','Sociology','Mathematics']
  
    
    
    df_exploded = df.explode('fieldOfStudy')
    grouped = df_exploded.groupby('fieldOfStudy')
       
    newDF = []
    
    for fieldOfStudy, group in grouped:
        print(type(group))
        
        newDF.append(group)
        # print(fieldOfStudy , " : " , len(group))
    
    combined_df = pd.concat(newDF)
    combined_df = combined_df.reset_index(drop=True)
    print(combined_df.head())
    combined_df.to_parquet("groupedDataset.parquet")


    # for field in fields:

    #     if field in df["fieldOfStudy"]:
            
    print("--- %s seconds ---" % (time.time() - start_time))

    
    print(f"RAM used: {psutil.Process().memory_info().rss / (1024 * 1024):.2f} MB")
    df.memory_usage() 
    return df



def loadDataByYear():
    df = pd.read_parquet("dataset.parquet")
    grouped = df.groupby('year')
    newDF = []      
    for year, group in grouped:
        newDF.append(group)
        print(year , " : " , len(group))

# Process.memory_info is expressed in bytes, so convert to megabytes


# load_data()
loadDataByYear()

