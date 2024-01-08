import polars as pl
import pandas as pd
import json

def readFile():
    df = pl.read_parquet("/dataHDD1/pmData/s2orcParsed/combinedPapers.parquet")
    df_exploded = df.explode('s2fieldsofstudy')
    exploded_list = [i for i in df_exploded["s2fieldsofstudy"]]
    df_sep = pl.from_dicts(exploded_list)
    df_res = df_exploded.with_columns(df_sep)
    df_filter = df_res.filter(pl.col("source") == "external")
    grouped = df_filter.groupby('category')
    
    results = []
    records = []
    for cat, group in grouped:
        res = getCitationCountBF(cat,group)
        records.append(res[0])
        results.append(res[1])

    resultBF = pl.concat(results)    
    
    print(len(resultBF))
        
    jsonRecords = json.dumps(records, indent=4)
    
    with open("binInfoWidth.json", "w") as outfile:
        outfile.write(jsonRecords)

    records = []
    results = []
    for cat, group in grouped:
        res = getCitationCountDF(cat,group)
        records.append(res[0])
        results.append(res[1])
        
    resultDF = pl.concat(results)
    
    print(len(resultDF))
        
    jsonRecords = json.dumps(records, indent=4)
    
    with open("binInfoDepth.json", "w") as outfile:
        outfile.write(jsonRecords)

def getCitationCountDF(cat,group):
    size = int(len(group["citationcount"]) / 5)
    bins = []
    dfList = []
        
    for ind,i in enumerate(range(0, len(group["citationcount"]), size )):
        tempDf = pl.DataFrame()
        group = group.sort(["citationcount"]) 
        selectedGroup = group[i: i + size]
        tempDf = tempDf.with_columns(id = pl.lit(selectedGroup["corpusid"]))
        tempDf = tempDf.with_columns(field = pl.lit(cat))
        tempDf = tempDf.with_columns(bin = ind)
        bin = {"max":max(selectedGroup["citationcount"]), "min":min(selectedGroup["citationcount"]),"bin": ind, "total_records": len(selectedGroup)}     
        bins.append(bin)
        dfList.append(tempDf)

    dfJoined = pl.concat(dfList)

    return ({cat: bins},dfJoined)


def getCitationCountBF(cat,group):
    rn = int((max(group["citationcount"]) - min(group["citationcount"]))/ 5)
    bins = []
    bfList = []

    for ind,i in enumerate(range(min(group["citationcount"]), max(group["citationcount"]), rn )):
        tempDf = pl.DataFrame()
        group = group.sort(["citationcount"])        
        filtered = group.filter((pl.col("citationcount") >= i) & (pl.col("citationcount") < i + rn))

        total =  len(filtered["citationcount"]) if not filtered.is_empty() else 0

        tempDf = tempDf.with_columns(id = pl.lit(filtered["corpusid"]))
        tempDf = tempDf.with_columns(field = pl.lit(cat))
        tempDf = tempDf.with_columns(bin = ind)
        
        bin = {"min":i,"max":i + rn - 1, "bin": ind, "total_records": total}
        
        bins.append(bin)
        bfList.append(tempDf)

    bfJoined = pl.concat(bfList)

    return ({cat: bins},bfJoined)
    

if __name__ == '__main__':
    readFile()