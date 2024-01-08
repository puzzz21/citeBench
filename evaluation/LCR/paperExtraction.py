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
    def __init__(self, datasetname):
        self.datasetname = datasetname
    
    def run(self):
        data = pl.read_json(f"{self.datasetname}/{self.datasetname}.json")
        result1 = data['citedPaper'].to_list()
        result2 =  data['citingPaper'].to_list()
        result = result1 + result2

        title1 = [t["title"] for t in data["citedPaperMetaInfo"].to_list()]
        title2 = [t["title"] for t in data["citingPaperMetaInfo"].to_list()]
        titles = title1 + title2
        
        paperAbs = self.getAbstract(result, titles)
        print(paperAbs)

        paperAbsObj = {}

        for item in paperAbs:
            i = json.loads(json.dumps(item))
            ind = next(iter(i))
            paperAbsObj[ind] = i[ind]
        
        with open(f'{self.datasetname}/papers{self.datasetname}.json', 'w') as f:
            json.dump(paperAbsObj, f)
            
        #removing the records from dataset that does not have abstract
        filteredDS = self.filterDS(paperAbs)
        with open(f'{self.datasetname}/final{self.datasetname}.json', 'w') as output_file:
            json.dump(filteredDS, output_file, indent=2)
    
    def getAbstract(self, result, titles):
        abstractData = []

        for i in range(30):
            df = pl.read_parquet(f"/local/s2orc/{i}.parquet")
            res = df.filter(pl.col("corpusid").is_in(result))
            ids = res['content.source.pdfsha'].to_list()
            
            res = df.filter(pl.col("corpusid").is_in(result))
            # resSelect = res.select(["content.text","content.annotations.abstract"])
            ddd = res.to_pandas()
            dx = pd.DataFrame(ddd)
            indx = dx["content.annotations.abstract"]
            for index,i in enumerate(indx):
                if i is not None:
                    idata = json.loads(i)[0]
                    abstract = dx["content.text"][index][int(idata["start"]):int(idata["end"])]
                    if "citation:" not in abstract.lower():
                        abstractData.append(abstract)
                    else:
                        abstractData.append(None)
                else:
                    data = ar.getMetaInfo(dx['content.source.pdfsha'][index])
                    if 'abstract' in data and data["abstract"]:
                        abstractData.append(data["abstract"])
                    else:
                        abstractData.append(None)

        finalRes = []
        for i in range(len(abstractData)):
            if abstractData[i] is not None:
                obj = {result[i]: {"title": titles[i], "abstract": abstractData[i]}}
                finalRes.append(obj)
                
        return finalRes

    def filterDS(self,finalRes):
        keys = []
        for r in finalRes:
            first_key = next(iter(r))
            keys.append(first_key)
            
        # Parse the JSON array
        with open(f"{self.datasetname}/{self.datasetname}.json", 'r') as file:
            json_array = json.load(file)
        final = []
        # Loop through the JSON array
        for item in json_array:
            if item["citedPaper"] in keys:
                final.append(item)
        
        return final
                

    
if __name__ == "__main__":
    process()
