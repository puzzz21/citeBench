import multiprocessing as mp
import polars as pl
import pandas as pd
import json
import time

def process_line(chunk):
    try:
        dfs = []  # Initialize with an empty DataFrame

        for line in chunk:
            json_data = json.loads(line)
            df = pd.DataFrame(pd.json_normalize(json_data))

            dfs.append(df)
            
        
        if len(dfs) > 1:  # Check if there is data to concatenate
            result_df = pd.concat(dfs)
            return result_df
        
        return None
    except json.JSONDecodeError:
        return None
    except pl.ShapeError:
        return None
    except pl.DuplicateError:
        return None

def read_lines(filename, chunk_size):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Split lines into chunks
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    return chunks

def read_file_and_convert_to_df(fp):
    num = mp.cpu_count()
    chunk_size = 10000
    chunks = read_lines(fp, chunk_size)
    print(len(chunks))
    
    with mp.Pool(processes=num) as pool:
        results = pool.map(process_line, chunks)

    # Filter out any None values from the results list
    results = [df for df in results if df is not None]
    
    if results:
        final_df = pd.concat(results)
        print(final_df)
        return final_df
    
    return None

start_time = time.time()  # Record start time

for i in range(30):
    file_path = str(i) + '.txt'

    dataframe = read_file_and_convert_to_df(file_path)

    if dataframe is not None:
        print(len(dataframe))
        dataframe.to_parquet(str(i) +".parquet")
    else:
        print("No dataframes to concatenate")

end_time = time.time()
processing_time = end_time - start_time
print(f"Processing time: {processing_time:.2f} seconds")
print(dataframe)