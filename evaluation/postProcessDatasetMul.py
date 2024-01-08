import json
import codecs
import polars as pl

combined = "../diagnostic_stats/dataset/combinedPapers.parquet"
p = pl.read_parquet(combined)
# get data
def postprocessData(): 
    
    with open('mulCitedMetaData.json') as data_file:    
        mulData = json.load(data_file)
        postProcessedMulData = []
        for data in mulData:
            text = data["context"]
            
            data["context"] = codecs.decode(text, 'unicode_escape').strip()
            data["context"] = data["context"].replace("<ref>","<REF>")
            if data["class"] == "grouped":
                context = data["context"]
                refTokenCount = context.count("<REF>")
                
                refStr = ""
                if refTokenCount != data["refCount"]:
                    
                    for i in range(data["refCount"]):
                        refStr += "<REF>"
                    
                    context = context.replace("<REF>",refStr)
                    data["context"] = context
                
            
            
            data["citingPaperMetaInfo"] = getMetaInfo(data["metaData"])
            
            citedMeta = []
            for ref in data["ref"]:
                citedRef = getMetaInfo(ref)
                citedMeta.append(citedRef)
                
            data["citedPaperMetaInfo"] = citedMeta
            
            if len(citedMeta) == data["refCount"]:
                del data["ref"]
                del data["metaData"]
                data["field"] = data["feild"]
                del data["feild"]
                postProcessedMulData.append(data)

            
                
            
            
            
    #         newLoc.append(data)


    file_path = "postProcessedMul.json"

    # #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(postProcessedMulData, json_file, indent=4,ensure_ascii=False) 

def getMetaInfo(metaData):
    if "authors" in metaData:
        metaData["author"] = metaData["authors"]
    lenName = len(metaData["author"][0].split(" "))
    auth = metaData["author"][0].split(" ")[lenName - 1]
    title = metaData["title"]
    if "year" not in metaData:
        metaData["year"] = None
        
    year = metaData["year"]

    if "citationCount" not in metaData:
        metaData["citationCount"] = None
    cc = metaData["citationCount"]
    venue = metaData["venue"]
    authors = metaData["author"]
    paperMeta = {"firstAuthor": auth, "authors":authors, "title":title, "year":year,"citationcount":cc,"venue":venue}
    return paperMeta
    
#     ['corpusid',
#  'externalids',
#  'url',
#  'title',
#  'authors',
#  'venue',
#  'publicationvenueid',
#  'year',
#  'referencecount',
#  'citationcount',
#  'influentialcitationcount',
#  'isopenaccess',
#  's2fieldsofstudy',
#  'publicationtypes',
#  'publicationdate',
#  'journal']

# parse wierd characters


# retrieve necessary info


if __name__ == '__main__':
    postprocessData()
