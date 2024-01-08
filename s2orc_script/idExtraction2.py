import spacy
import sys
import polars as pl
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc
from API_request import APIRequest as ar
import pandas as pd
import json
import time
import multiprocessing as mp
from pymongo import UpdateOne

# def extractIds():
#     num = mp.cpu_count()

#     with mp.Pool(processes=num) as pool:
#         results = pool.map(process, range(30))
        
def extractIds():
    db = mc.connect()
    chunkSize = 50
    for i in range(16,30):
        print("--------------------------")
        print("file: ", str(i))
        data = pl.read_parquet("/dataHDD1/pmData/news2cDownloads/"+ str(i) + ".parquet")
        ids = data["content.source.pdfsha"].to_list()
        count = 0 
        for j in range(0, len(ids), chunkSize):

            k = 0
            while k < 1  :
                chunk = ids[j:j + chunkSize]
                docs = ar.getMetaBatch2(chunk)
                # filtered_data_list = [doc for doc in docs if isinstance(doc, dict)]
                filtered_data_list = []
                print("docs: ", len(docs))
                print(docs)
                if len(docs) > 10:
                    # filteredData = []
                    for t,doc in enumerate(docs):
                        if isinstance(doc, dict):
                            doc["updated"] = 1
                            doc["chunk"] = i
                            filtered_data_list.append(doc)
                        else:
                            if chunk[t] != None:
                                filtered_data_list.append({ "paperId": chunk[t], "updated": 0, "chunk": i})
                            else:
                                count += 1
                
                                    

                        #     doc["updated"] = 1
                        #     doc.update(filtered_data_list)
                        # else:
                        #     doc["updated"] = 0
                        
                            
                        # mc.bulk_save(db,"apiData",filtered_data_list)
                        k += 1
                else:
                    time.sleep(1)
            print("filtered_data_list: ", len(filtered_data_list))
            # mc.bulk_save(db,"apiData",filtered_data_list)
        if count > 0:
            with open("err.txt", "a") as f:
                f.write("\n Count of file " + str(i) + ' ::: ' + str(count))
                    


def saveMeta():
    db = mc.connect()
    chunkSize = 10000
    for i in range(0,30):
        data = pl.read_parquet("/dataHDD1/pmData/s2orcDownloads/"+ str(i) + ".parquet")
        ids = data["content.source.pdfsha"].to_list()
        for j in range(0, len(ids), chunkSize):
            chunk = ids[j:j + chunkSize]
            objList = [{"pId": id, "updated": 0} for id in chunk]
            mc.bulk_save(db,"meta",objList)
            
def process_data(data_chunk, db):
    bulk_updates = []
    for d in data_chunk:
        print(d["paperId"])
        query = {"pId": d["paperId"]}
        del d["paperId"]
        del d["_id"]
        obj = {"$set": {"data": d, "updated": 1}}
        bulk_updates.append(UpdateOne(query, obj))

    if bulk_updates:
        mc.update_bulk(db, "meta", bulk_updates)
        
    # print("hi!")
    # print("i am here")
    # for d in data_chunk:
    #     print(d["paperId"])
    #     query = {"pId": d["paperId"]}
    #     del d["paperId"]
    #     del d["_id"]
    #     obj = {"$set": {"data": d, "updated": 1}}
    #     mc.update(db, "meta", query, obj)
        
def updateMeta():
    db = mc.connect()

    chunkSize = 10000
    for i in range(0, 516234, chunkSize):
        data = mc.retrieve_records(db,"metadata",i, i + chunkSize)
        
        cs = 500
        num_processes = mp.cpu_count()  # Get the number of available CPU cores.


        # Split data into chunks, one chunk per process/thread.
        data_chunks = [data[j:j + cs] for j in range(0, len(data), cs)]

        processes = []
        for i in range(min(num_processes, len(data_chunks))):
            data_chunk = data_chunks[i]

            p = mp.Process(target=process_data, args=(data_chunk, db))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
        
        
        # for d in data:
        #     print(d["paperId"])
        #     query = {"pId":d["paperId"]}
        #     del d["paperId"]
        #     del d["_id"]
        #     obj = { "$set": { "data": d, "updated":1}}                
        #     mc.update(db,"meta",query,obj)
        
    
def test():
    count = 0
    for i in range(0,30):
        print(i)
    #     data = pl.read_parquet("/dataHDD1/pmData/s2orcDownloads/"+ str(i) + ".parquet")
    #     count += len(data)
    # print(count)


if __name__ == "__main__":
    extractIds()
