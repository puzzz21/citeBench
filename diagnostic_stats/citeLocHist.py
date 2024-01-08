import matplotlib.pyplot as plt
from pymongo import MongoClient
import mongoConnect as mc
import json
import numpy as np
# Connect to MongoDB
# 
# db = mc.connect()

# data = mc.retrieveCiteLoc(db, "citedDataTemp")


with open('citeLoc.txt', 'r') as file:
    lines = file.readlines()
    t = ""
    for line in lines:
        t = t + line.strip()
d = []


# Sample data
t = t.replace("[","").replace("]","")

x = [float(x) for x in t.split(", ")]

data = np.array(x)

print(len(data))

# Calculate the frequency of each number
hist, bins = np.histogram(data)

# Create the histogram using matplotlib
plt.hist(data, density=False, rwidth=0.9, alpha=0.75)
plt.xlabel('Position')
plt.ylabel('Frequency')
plt.title('Citation position distribution among the sentences')
plt.savefig("hist.png")


# data = mc.retrieveWithCondition(db, "citedData","tokenLen")
# file = open('tokenLen.txt','w')
# file.writelines(str(data))
# file.close()


# # Retrieve parameter values from MongoDB

# sorted_data = sorted(data)
# n = len(sorted_data)
# q1_index = int(n * 0.25)
# q3_index = int(n * 0.75)
# q1 = sorted_data[q1_index]
# q3 = sorted_data[q3_index]
# iqr = q3 - q1
# lower_bound = q1 - (5 * iqr)
# upper_bound = q3 + (5 * iqr)
# filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

# print(filtered_data)

# plt.hist(filtered_data, bins=1000)
# plt.xlabel("Parameter Value")
# plt.ylabel("Frequency")
# plt.title("Distribution of Parameter Value")
# plt.xlim(min(filtered_data), max(filtered_data))

# print(max(filtered_data))

# plt.savefig("plot.png")

# # Close the MongoDB connection