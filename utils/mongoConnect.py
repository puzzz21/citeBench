from pymongo import MongoClient


CONNECTION_STRING = "mongodb://muser:iamuser@127.0.0.1:27017/citation"


def get_connect():
    client = MongoClient(CONNECTION_STRING)
    db = client["citation"]
    return db

def agg_query(colName,pipeline):
    db = get_connect()
    res = db[colName].aggregate(pipeline)
    return res


def insert_record(colName,obj):
    db = get_connect()
    col = db[colName]
    col.insert_one(obj)
    
    
def insert_many(colName, objs):
    db = get_connect()
    col = db[colName]
    col.insert_many(objs)

def get_records(colName,query):
    db = get_connect()
    col = db[colName]
     # Find records that match the query criteria
    results = col.find(query)
    return results

def connect():
    client = MongoClient(CONNECTION_STRING)
    db = client["citation"]
    return db

def update_bulk(db, colName, objs):
    col = db[colName]
    col.bulk_write(objs, ordered=False)

    
def save_record(db,colName,obj):
    col = db[colName]
    result = col.insert_one(obj)
    obj_id = result.inserted_id
    
    return obj_id

def bulk_save(db,colName,objs):
    col = db[colName]
    col.insert_many(objs)

def retrieve_records(db,colName, start, end = None):
    col = db[colName]
    print(start)
    
    # if all((start,end)):
    docs = col.find().skip(start).limit(end)
    # else:
    #     docs = col.find()
        
    return list(docs)

def read_records(colName):
    db = get_connect()

    col = db[colName]
    
    # if all((start,end)):
    docs = col.find()
    # else:
    #     docs = col.find()
        
    return list(docs)


def total_records(db,colName):
    col = db[colName]
    total_documents = col.count_documents()
    return total_documents

def count_records(colName,query):
    db = get_connect()
    col = db[colName]
    total_documents = col.count_documents(query)
    return total_documents

def save_many(db,colName, objs):
    print("hello")
    col = db[colName]
    col.insert_many(objs)
    
def update(db,colName, query, objs):
    col = db[colName]
    
    col.update_one(query, objs)
    

    
def retrieveTokenLen(db,colName):
    col = db[colName]
    # if all((start,end)):
    parameter_values = []
        
    for doc in col.find({"citeInfo": {'$exists': True}}):
        parameter_values.append(doc["citeInfo"]["tokenLen"])
    
    return parameter_values

def retrieveCiteLoc(db,colName):
    col = db[colName]
    # if all((start,end)):
    parameter_values = []
        
    for doc in col.find({"citeInfo.tokenClass": {'$exists': True}}):
        if doc["citeInfo"]["tokenClass"] == "mean":
            parameter_values.append(doc["citeInfo"]["citeLocation"] / doc["citeInfo"]["tokenLen"])
    
    return parameter_values

def retrievePOSBefore(db,colName):
    col = db[colName]
    # if all((start,end)):
    parameter_values = []
        
    for doc in col.find({"citeInfo.POSWordBefore": {'$exists': True},"$and": [
    { "citeInfo.POSWordBefore": { "$ne": '""' } },
    { "citeInfo.POSWordBefore": { "$ne": "''" } },
    { "citeInfo.POSWordBefore": { "$ne": '``' } },
    { "citeInfo.POSWordBefore": { "$ne": ":" } }
  ]}):
        parameter_values.append(doc["citeInfo"]["POSWordBefore"])
    
    return parameter_values

def filterTokenLen(db,colName,section1,section2,section3):
    col = db[colName]
    up = []
    lo = []
    mean = []
    # if all((start,end)):
    for doc in col.find({}, {"citeInfo": 1}):
        if "citeInfo" in doc:
            if "tokenLen" in doc["citeInfo"]:
                if doc["citeInfo"]["tokenLen"] in section3:
                    doc["citeInfo"]["tokenClass"] = "upper"
                    ob = { "$set": { "citeInfo": doc["citeInfo"] } }
                    
                    update(db,"citedData",{"_id": doc["_id"]}, ob)
                    up.append(doc["_id"])
                elif doc["citeInfo"]["tokenLen"] in section2:
                    doc["citeInfo"]["tokenClass"] = "mean"
                    ob = { "$set": { "citeInfo": doc["citeInfo"] } }
                    update(db,"citedData",{"_id": doc["_id"]}, ob)
                    lo.append(doc["_id"])
                elif doc["citeInfo"]["tokenLen"] in section1:
                    doc["citeInfo"]["tokenClass"] = "lower"
                    ob = { "$set": { "citeInfo": doc["citeInfo"] } }

                    update(db,"citedData",{"_id": doc["_id"]}, ob)
                    mean.append(doc["_id"])
    
    
    return {"upper": up, "lower": lo, "mean": mean}

    # return col.find({}, {"citeInfo.tokenLen": 1})
    
def extractPapersForFields(db):
    fields = ["Art", "Biology","Business", "Chemistry", "Computer Science", "Economics",
"Engineering", "Environmental Science", "Geography", "Geology", "History",
"Materials Science", "Mathematics", "Medicine", "Philosophy", "Physics",
"Political Science", "Psychology", "Sociology"]
    papers = db["papers"]
    results = []
    ids = []
    try:

        for field in fields:
            res = []
            
            pipeline = [
                { "$match": { "fieldsOfStudy": { "$elemMatch": { "$in": [field] } }, "paperId": { "$nin": ids } } },
                { "$sample": { "size": 150 } }
            ]

            sampled_records = list(papers.aggregate(pipeline))
            print(len(sampled_records))
            for recs in sampled_records:
                ids.append(recs["paperId"])
                res.append(recs)
                
                
                
            # paps = papers.find({"fieldsOfStudy": {"$elemMatch": {"$in": [field]}},"paperId": { "$nin": ids }}).limit(200)
            # for pap in paps:
            #     ids.append(pap["paperId"])
            #     res.append(pap)
                
            results.append({field: res})
                
    except Exception as e:
        print(f"An error occurred: {e}")
    # print(results)
    return results
        
        
            
def extractCitedData(db):
    
    cited = db["citedData"]
    results = []
    ids = []
    try:

            res = []
            
            pipeline = [
                { "$sample": { "size": 100 } }
            ]

            sampled_records = cited.aggregate(pipeline)

                
                
                
            # paps = papers.find({"fieldsOfStudy": {"$elemMatch": {"$in": [field]}},"paperId": { "$nin": ids }}).limit(200)
            # for pap in paps:
            #     ids.append(pap["paperId"])
            #     res.append(pap)
                
            results.append(sampled_records)
                
    except Exception as e:
        print(f"An error occurred: {e}")
    # print(results)
    return results            
            
            
            
    
def filterForTokenLen(db,colName):
    col = db[colName]
        
    # query = col.find({'citeInfo.tokenClass': {'$exists': True}})

    # uniqueId = []
    
    pipeline = [
        {'$match': {'citeInfo.tokenClass': {'$exists': True}}},
        {'$group': {'_id': '$paperId','tokenClass': {'$addToSet': '$citeInfo.tokenClass'} }},
        {'$unwind': '$tokenClass'}
    ]

    results = col.aggregate(pipeline, allowDiskUse=True)

    count = 0
    # Process the results
    for result in results:
        
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'paperId': result["_id"]},
                        {'citeInfo.tokenClass':result["tokenClass"]}
                    ]
                }
            },
            {
                '$limit': 1
            }
        ]

        data = col.aggregate(pipeline)
     
        # query = col.find({'paperId': result["_id"]}, {'citeInfo.tokenClass': result["tokenClass"]})
        for d in data:
            count = count + 1
            # d["citeInfo"]["tokenPaperSelected"] = True
            # ob = { "$set": { "citeInfo": d["citeInfo"] } }
            # update(db,"citedData",{"_id": d["_id"]}, ob)
        
        
        # select = result["cited"][0]
        
        # select["citeInfo"]["tokenPaperSelected"] = True
        # ob = { "$set": { "citeInfo": select["citeInfo"] } } 
         
        # update(db,"citedData",{"_id": select["_id"]}, ob)
        count = count + 1
        
    print(count)
    
    # # Retrieve unique values for the field
    # for doc in query:
        
                
    #     if str(doc["paperId"]) not in uniqueId:
    #         uniqueId.append(str(doc["paperId"]))
    #         cl = []
    #         c = doc["citeInfo"]["tokenClass"]
    #         for i in ["upper","mean","lower"]:
                
    #             if c not in cl:      
    #                 cl.append(i)   
    #                 doc["citeInfo"]["tokenPaperSelected"] = True
    #                 ob = { "$set": { "citeInfo": doc["citeInfo"] } }
                            
    #                 update(db,"citedData",{"_id": doc["_id"]}, ob)
        #     print(doc["_id"])
        #     print(doc["citeInfo"]["tokenClass"])
        
    return 1
        
def filterByField(db,colName):
    fields = ["Art", "Biology","Business", "Chemistry", "Computer Science", "Economics",
"Engineering", "Environmental Science", "Geography", "Geology", "History",
"Materials Science", "Mathematics", "Medicine", "Philosophy", "Physics",
"Political Science", "Psychology and Sociology"]
    col = db[colName]
    colPaper = db["papers"]
    
    papers = db['papers']
    lowest_countmin = []

    for field in fields:
        print(field)
        pipeline = [
    {
        '$lookup': {
            'from': 'papers',
            'localField': 'paperId',
            'foreignField': '_id',
            'as': 'paper'
        }
    },
    {
        '$match': {
            '$and': [
                {"paper.fieldsOfStudy": {"$in": [field]}},
                {'citeInfo.tokenClass': {'$exists': True}}
            ]
        }
    }
]

        results = col.aggregate(pipeline)
        # print(results)

# Process the results
        lower = 0
        upper = 0
        mean = 0
        for result in results:
            if result["citeInfo"]["tokenClass"] == "lower":
                lower = lower + 1
            elif result["citeInfo"]["tokenClass"] == "upper":
                upper = upper + 1
            elif result["citeInfo"]["tokenClass"] == "mean":
                mean = mean + 1
        
        if(min(upper, mean, lower) != 0):
            lowest_countmin.append(min(upper, mean, lower))
            lowest_count = min(lowest_countmin)
    print(lowest_count)
    print("=======================================")
        
        
        # paperQuery = colPaper.find({'fieldsOfStudy': {'$in': [field]}})
        # for q in paperQuery:
        #     query = col.count({'citeInfo.tokenPaperSelected': {'$exists': True}, 'paperId': q["_id"],'citeInfo.tokenClass': 'upper'})
        #     print(query)


    # Perform the aggregation
        # query = col.find({'citeInfo.tokenPaperSelected': {'$exists': True}})

        # # Print the matched documents
        # for result in query:
        #     q = colPaper.find({'paperId': result["paperId"], 'fieldsOfStudy': {'$in': [field]}})

        #     print(q)
    
    
    # query = col.find({'citeInfo.tokenPaperSelected': {'$exists': True}})

    # for field in fields:

    #     paperQuery = colPaper.find({'fieldsOfStudy': {'$in': [field]}})
        
    #     # paperQuery = colPaper.count({'fieldsOfStudy': {'$in': [field]}})
    #     # paperQuery = colPaper.count({'fieldsOfStudy': {'$in': [field]}})
    #     # paperQuery = colPaper.count({'fieldsOfStudy': {'$in': [field]}})
        
    #     for doc in paperQuery:
    #         print(doc["paperId"])
            


    #     print(field, paperQuery)
        # for doc in paperQuery:
        #     print(doc)

        # for doc in query:
            
        #     print(doc)
    
def aggregateData(colName,pipeline):
    db = get_connect()
    col = db[colName]
    results = col.aggregate(pipeline)
    return results
    
    
def filterByFieldY(db,colName):
    fields = ["Biology","Chemistry", "Computer Science",
"Materials Science", "Mathematics", "Medicine", "Physics"]
    
    col = db[colName]
    colPaper = db["papers"]
    
    papers = db['papers']
    lowest_countmin = []

    for field in fields:
        for year in [(1996, 2000), (2001, 2005), (2006, 2010), (2011, 2015), (2016, 2020)]:
            for c in [2,3,4,5,6,7,8,9,10,11]:
                print(field)
                
                sizeQuery = {"ref": {"$exists": True, "$size": c}}


                
                pipeline = [
            {
                '$lookup': {
                    'from': 'papers',
                    'localField': 'paperId',
                    'foreignField': '_id',
                    'as': 'paper'
                }
            },
            {
                '$match': {
                    '$and': [
                        {"paper.fieldsOfStudy": {"$in": [field]}},
                        {"paper.year": {"$gte": year[0], "$lte": year[1]}},
                        # {'citeInfo.tokenClass': {'$exists': True}},
                        sizeQuery
                    ]
                }
            }
        ]

                results = col.aggregate(pipeline)
                for result in results:
                    print(len(result["ref"]))  
    
    

    
  
# # This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
   # Get the database
   db = get_connect()
   filterByFieldY(db,"citedData")