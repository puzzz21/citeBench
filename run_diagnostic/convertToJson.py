from bson.json_util import dumps
from pymongo import MongoClient
import sys
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc

if __name__ == '__main__':
    diagnostic_col = ["finalWorthsss","finalLengths","finalLocations","finalLow","finalPosWords","finalIntents"]
    diagnostic_file = ["worth","length","location","low","posWord","intent"]
    
    for i,item in enumerate(diagnostic_col):
        data = mc.read_records(diagnostic_col[i])
        json_data = dumps(data, indent = 2)  
        with open(diagnostic_file[i] + ".json", 'w') as file: 
            file.write(json_data)