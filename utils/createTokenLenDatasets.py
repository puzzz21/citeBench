import numpy as np
from pymongo import MongoClient
import mongoConnect as mc

import matplotlib.pyplot as plt
from scipy.stats import norm

db = mc.connect()


# Connect to the MongoDB server

# data = mc.filterForTokenLen(db, "citedData")
data = mc.filterByField(db, "citedData")

print(data)