import json
import re
import sys
import click
import json
sys.path.append("/abyss/home/citation-recommendation/utils")
import mongoConnect as mc
import pandas as pd

dataClasses = {
    "length" : ["short", "medium", "long"],
    "position" : ["start", "middle", "end"],
    "intent" : ["background", "methodology", "result"],
    "worth" : ["comma","period"],
    "pos" : ["before_verb","before_noun","before_adjective","before_adverb","before_pronoun","before_preposition","before_others",
             "after_verb","after_noun","after_adjective","after_adverb","after_pronoun","after_preposition","after_others"],
    "low":[]
}

docName = {
    "intent": ["citedType","citingType","citingTextType","finalIntents"],
    "position":["citedLoc","citingLoc","citingTextLoc","finalLocations"],
    "worth":["citedWorthNew","citingWorthNew","citingTextWorthNew","finalWorthsss"],
    "length":["citedLength","citingLength","citingTextLength","finalLength"],
    "pos":["citedPosWords","citingPosWords","citingTextPosWords","finalPosWords"],
    "low":["citedLow","citingLow","citingTextLow","finalLow"]
}

fields = ["Biology","Chemistry","Computer Science","Medicine","Materials Science","Physics", "Mathematics"]
years = [(1996,2000),(2001,2005),(2006,2010),(2011,2015),(2016,2020)]


@click.command()
@click.option("--datasetname", required=True, type=click.Choice(['length', 'position', 'intent',"worth", "pos"]), 
              help="Name of the dataset. Pick among length, position, and intent")

def process(datasetname):
    dg = RetrieveMissing(datasetname)
    dg.run()

class RetrieveMissing:
    def __init__(self, datasetname):
        self.datasetname = datasetname
    
    def run(self):
        """
            Processes Dataset for each fields in the multiprocesses, parallely
        """
        

        with open("../dataset/"+self.datasetname+".json") as json_file:
            json_data = json.load(json_file)
            
        res = []
        classes = []
        df = pd.json_normalize(json_data)
        df["year"] = df["year"]
        
        df["year"] = df["year"].str[0]
        df['context'] = df['context'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)


        for field in fields:
            for year in years:
                for i in range(10):   
                    classes = []
                    # df['field'] == field &                  df["group"] == i
                    rslt_df = df.loc[(df['field'] == field) & (df["year"] == year[0]) & (df["group"] == i)]
                    
                    if len(rslt_df) > 0:
                        
                        # print(len(rslt_df["context"]))
                        for j in range(len(rslt_df["context"])):
                            if self.datasetname == "pos":
                                classes.append(rslt_df.iloc[j]["selectedPOSClass"])
                            elif self.datasetname == "intent":
                                obj = rslt_df["context"].iloc[j][0]
                                if "intentClass" in obj:
                                    classes.append(obj[self.datasetname  + "Class"])
                            else:
                                classes.append(rslt_df["context"].iloc[j][0][self.datasetname  + "Class"])
                                
                    set1 = set(dataClasses[self.datasetname])
                    set2 = set(classes)
                    # print(set2)
                                                                                                         
                    difference = list(set1 - set2)
                    if len(difference) > 0:
                        for c in difference:
                            temp = {"field": field, "year":year, "group": i, "class":c}
                            res.append(temp)
        # print(res)
        
        
                    # # for c in dataClasses["length"]:
                    # for data in json_data:
                    #     # print(data["context"][0]["lengthClass"])
                        
        #             #     if data["field"] == field and list(data["year"]) == list(year) and data["group"] == i:
        #             #         if data["context"][0]["lengthClass"] != None:
        #             #             classes.append(data["context"][0]["lengthClass"])
        #             #     # elif data["field"] == field and list(data["year"]) == list(year) and data["group"] == i:
                            
                        

        #             # set1 = set(dataClasses["length"])
        #             # set2 = set(classes)
                    
        #             # difference = list(set1 - set2)
        #             # if len(difference) > 0:
        #             #     for c in difference:
        #             #         print(c)
        #             #         temp = {"field": field, "year":year, "group": i, "class":c}
                    
        #             #         res.append(temp)
                        
        with open('../dataset/missing' + self.datasetname + '.json', 'w') as f:
            json.dump(res, f)
                                
                                
if __name__ == "__main__":
    process()