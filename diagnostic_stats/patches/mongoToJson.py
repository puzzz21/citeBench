from bson.json_util import dumps
import sys
sys.path.append("/home/pop533611/citation-recommendation/utils")
import mongoConnect as mc

if __name__ == '__main__':
    records = mc.get_records("finalWorthssss",{})
    with open('finalWorthssss.json', 'w') as file:
        file.write('[')
        for document in records:
            file.write(dumps(document))
            file.write(',')
        file.write(']')
