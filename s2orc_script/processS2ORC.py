import polars as pl
import pandas as pd
import json
import time
import subprocess

def process_line(chunk):
    try:
        dfs = []  # Initialize with an empty DataFrame

        for line in chunk:
            json_data = json.loads(line)
            df = pd.DataFrame(pd.json_normalize(json_data))

            dfs.append(df)
            
        if dfs:  # Check if there is data to concatenate
            result_df = pd.concat(dfs)
            return result_df
        
        return None
    except json.JSONDecodeError:
        return None
    except pl.ShapeError:
        return None
    except pl.DuplicateError:
        return None

def read_file_and_convert_to_df(fp):
    dfs = []
    try:
        with open(fp, 'r') as file:
            for line in file:
                json_data = json.loads(line)
                df = pd.DataFrame(pd.json_normalize(json_data))
                dfs.append(df)
                print("df: ", len(dfs))
        
        result_df = pd.concat(dfs)
        
        if result_df is not None:
            result_df.to_parquet(fp.replace('.txt', '.parquet'))
        
    except FileNotFoundError:
        print(f"File not found: {fp}")
        return None

start_time = time.time()  # Record start time

for i in range(30):
    file_path = f"/local/s2orc/{i}.txt"
    read_file_and_convert_to_df(file_path)
    cmd = ["rm","-rf",file_path]
    subprocess.run(cmd, check=True)
    


end_time = time.time()
processing_time = end_time - start_time
print(f"Processing time: {processing_time:.2f} seconds")
