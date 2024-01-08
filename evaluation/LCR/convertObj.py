import polars as pl
import pandas as pd
import json
import click

import sys

sys.path.append("/abyss/home/citation-recommendation/utils")
from API_request import APIRequest as ar

@click.command()
@click.option("--dataset", required=True, type=click.Choice(['length', 'location', 'intent',"low", "pos"]), 
              help="Name of the dataset. Pick among length, position, and intent")

def process(dataset):
    with open(f"{dataset}/paper{dataset}.json", 'r') as file:
        json_array = json.load(file)
    
    data = {}
    print(json_array)

    # for item in json_array:
    #     # i = json.loads(json.dumps(item))
    #     print(item)
    #     # ind = next(iter(i))
    #     # print(ind, i )
    #     # data[ind] = i[ind]

    with open(f'{dataset}/paper{dataset}.json', 'w') as f:
        json.dump(data, f)
    
if __name__ == "__main__":
    process()
