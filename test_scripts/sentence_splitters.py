import spacy
import sys
import polars as pl
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc
import pandas as pd
import json
# nlp = spacy.load("en_core_sci_scibert")
db = mc.connect()

def extractPapers():
    papers = mc.extractPapersForFields(db)
    dataset = pl.scan_parquet("/dataHDD1/pmData/s2orcDownloads/0.parquet")

    resultDf = []
    
    for dict in papers:
        for key,values in dict.items():
            ids = []
            for value in values:
                ids.append(value["paperId"])
            res = dataset.filter(pl.col("content.source.pdfsha").is_in(ids)).collect()
            # print(pl.DataFrame(res)
            # res["field"] = key
            res = res.with_columns(pl.lit(key).alias("field"))
            
            

            # res.with_columns(field = pl.lit(key))
            
            print(res["field"])
            print(key)
            
            resultDf.append(res)
            
    df = pl.concat(resultDf)
    df.write_parquet("data_test.parquet")
    
def processPapers():
    dataset = pl.read_parquet("data_test.parquet")
    dataset.head()


    # def parse(self, data,db):
    #     # "bibref is the bib"
    #     text = data["content"]["text"]
    #     sentences = []
    #     paragraph = ""

    #     #  benepar.download('benepar_en3')
        
        

    #     if data["content"]["annotations"]["paragraph"] is not None:
    #         for i in json.loads(data["content"]["annotations"]["paragraph"]):
    #             paragraph += text[int(i["start"]): int(i["end"])].strip() + " "                
    #         try:
    #             doc = nlp(paragraph)
    #             for sentence in doc.sents:
    #                 # doc = nlp(sentence.text)
    #                 # if (list(doc.sents)[0]._.labels[0] == "S"):
    #                 if (len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric()):
    #                     sentences.append(sentence.text.strip())
                        

    #         except Exception as e:
    #             print(str(e))
    #             mc.save_record(db,"errors",{"error": str(e)})

    #     return sentences
        
        
    
if __name__ == '__main__':
    extractPapers()
    # processPapers()