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
    dg = DataGeneration(dataset)
    dg.run()

class DataGeneration:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def run(self):
        with open(f'{self.dataset}/final{self.dataset}.json') as data_file:    
            data = json.load(data_file)

        contextList = {}
        testList = []
        for d in data:
            citedPID = d["citedPaper"]
            citingPID = d["citingPaper"]
            sent = d["context"][0]["citedSent"].replace("<REF>","TARGETCIT")

            contextList[str(citedPID) + "_" + str(citingPID)] = {
                    "masked_text": sent,
                    "context_id": str(citedPID) + "_" + str(citingPID),
                    "citing_id": str(citedPID),
                    "refid": str(citingPID)
                    
            }
        
            testList.append({"context_id": str(citedPID) + "_" + str(citingPID), "positive_ids": [str(citingPID)]})

        with open(f'{self.dataset}/context{self.dataset}.json', 'w') as f:
            json.dump(contextList, f)  
            
        with open(f'{self.dataset}/test{self.dataset}.json', 'w') as f:
            json.dump(testList, f)
    
if __name__ == "__main__":
    process()