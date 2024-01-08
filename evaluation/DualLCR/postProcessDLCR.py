import json
import codecs
import polars as pl
import time
import pandas as pd
import click

@click.command()
@click.option("--dataset", required=True, type=click.Choice(['length', 'location', 'intent','worth','pos', "low"]),
              help="Name of the dataset. Pick among length, position, intent, worth, and pos")

def process(dataset):
    result = []
    
    with open(f'../dataset/{dataset}.json') as data_file:    
        data = json.load(data_file)

        for d in data:
            print(d)
            text = d["context"][0]["citedSent"]
            context = text.replace("<REF>","")
            title =  d["citedPaperMetaInfo"]["title"]
            authorsCited = ",".join(d["citedPaperMetaInfo"]["authors"])
            authorsCiting = ",".join(d["citingPaperMetaInfo"]["authors"])
            result.append({
                'context' : context, 
                'authors_citing' : authorsCiting, 
                'title_cited' : title, 
                'authors_cited': authorsCited
            })

    df = pd.json_normalize(result)
    df.to_csv(f"data/ncn{dataset}.csv",index=False)


if __name__ == '__main__':
    start_time = time.time()
    process()
    print("total time: ", time.time() - start_time)
