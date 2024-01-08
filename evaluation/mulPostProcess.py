import json
import codecs
import polars as pl

combined = "/dataHDD1/pmData/s2orcParsed/combinedPapers.parquet"
p = pl.read_parquet(combined)
# get data
def mulpostprocessData(): 
    
    with open('mulCitingMeta.json') as data_file:    
        locationData = json.load(data_file)
        newLoc = []        
        for data in locationData:
            text = data["context"]
            
            data["context"]= codecs.decode(text, 'unicode_escape').strip()
    #         print()
            
            
    #         # print(data)
    #         # print(decoded_text)
            data["citedPaperMetaInfo"] = getMetaInfo(data["citedPaper"])
            data["citingPaperMetaInfo"] = getMetaInfo(data["citingPaper"])
            newLoc.append(data)


    file_path = "postProcessedPOSAll.json"

    #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(newLoc, json_file, indent=4,ensure_ascii=False) 

def getMetaInfo(citedId):
 
    p_filter = p.filter((pl.col("corpusid") == citedId))

    author = p_filter[0]["authors"]

    lenName = len(author[0][0]["name"].split(" "))
    auth = author[0][0]["name"].split(" ")[lenName - 1]
    title = p_filter[0]["title"][0]
    year = p_filter[0]["year"][0]
    cc = p_filter[0]["citationcount"][0]
    venue = p_filter[0]["venue"][0]
    authors = p_filter[0]["authors"][0]
    ath = []
    for a in authors:
        ath.append(a["name"])
    paperMeta = {"firstAuthor": auth, "authors":ath, "title":title, "year":int(year),"citationcount":cc,"venue":venue}
    print(paperMeta)
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
    mulpostprocessData()
