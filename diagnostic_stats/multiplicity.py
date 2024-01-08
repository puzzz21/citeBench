import sys
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc
from multiple_citations import MultipleCitations 
from grouped_citations import GroupedCitation 


def getData():
    mul = MultipleCitations()
    gc = GroupedCitation()
    fields = ["Biology","Chemistry", "Computer Science",
"Materials Science", "Mathematics", "Medicine", "Physics"]

    for field in fields:
        print("--------------------------")
        print(field)
        for year in [(1996, 2000), (2001, 2005), (2006, 2010), (2011, 2015), (2016, 2020)]:
            print(year)
            for c in [2,3,4,5,6]:
                print("============================")
                print(c)
                
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

                results = mc.aggregateData("citedData",pipeline)
                grpList = []
                mulList = []
                for result in results:
                    for i in ["group", "multiple"]:
                        if i == "group":
                            d = gc.filterData(result["context"])
                            if d is not None and len(d[1]) > 0:
                                obj = {"year" : year, "feild": field, "refCount" : c, "class": "grouped","context": d[0],"cited": d[1], "citedId": result["_id"]}
                                mc.insert_record("mulDatas",obj)
                                grpList.append(d)
                        else:
                            d = mul.filterData(result["context"])
                            if d is not None and len(d[1]) > 0:
                                obj = {"year" : year, "feild": field, "refCount" : c, "class": "multiple","context": d[0],"cited": d[1], "citedId": result["_id"]}
                                mc.insert_record("mulDatas",obj)
                                mulList.append(d)
                    
                if len(grpList) == 20 and len(mulList) == 20:
                    break
                      

# # This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
   # Get the database
   getData()
