import sys
sys.path.append("/home/pop533611/thesis")
import pandas as pd
from pymongo import MongoClient
import mongoConnect as mc

ids = []
data = mc.read_records("citedLoc")
for d in data:
    if "corpusid" in d:
        ids.append(d["corpusid"])
data = mc.read_records("citedLen")
for d in data:
    if "corpusid" in d:
        ids.append(d["corpusid"])
data = mc.read_records("citedType")
for d in data:
    if "corpusid" in d:
        ids.append(d["corpusid"])

f = open("sampleIds.py", "w")
f.write("ids = " + str(ids))
f.close()