import matplotlib.pyplot as plt
from pymongo import MongoClient
import mongoConnect as mc
import json
import numpy as np
from collections import Counter

# Connect to MongoDB
# 
# db = mc.connect()

# data = mc.retrieveCiteLoc(db, "citedDataTemp")


with open('posBefore.txt', 'r') as file:
    lines = file.readlines()
    elemLine = ""
    for line in lines:
        elemLine = elemLine + line.strip()


# Sample data
elemLine = elemLine.replace("[","").replace("]","")

POSList = [str(elem.replace("'","")) for elem in elemLine.split(", ")]

verb = ['VB', 'VBD', 'VBG', 'VBP', 'VBZ', 'VBN']
noun = ['NN', 'NNS', 'NNP', 'NNPS']
adj = ['JJ', 'JJR', 'JJS']
adv = ['RB', 'RBR', 'RBS']
pronoun = ['PRP', 'PRP$','WP','EX']
preposition = ['IN','TO']
others = ['PDT','DT','CC','MD','WDT','POS','RP','FW','CD','WRB']

verbCat = [i for i in POSList if i in verb]
nounCat = [i for i in POSList if i in noun]
adjCat = [i for i in POSList if i in adj]
advCat = [i for i in POSList if i in adv]
pronounCat = [i for i in POSList if i in pronoun]
prepositionCat = [i for i in POSList if i in preposition]
othersCat = [i for i in POSList if i in others]


# mylist = list(set(x))
# print(mylist)

# POSList = Counter(POSList)

# data = np.array(elemLine)


# # Calculate the frequency of each number
# hist, bins = np.histogram(data)

# Create the histogram using matplotlib
# plt.xticks(rotation='vertical')
# plt.bar(list(POSList.keys()), POSList.values())
# plt.xlabel('POS')
# plt.ylabel('Frequency')
# plt.title('Histogram of POS')
# plt.show()
# plt.savefig("POSBeforeHist.png")

verbCount = len(verbCat)
nounCount = len(nounCat)
adjCount = len(adjCat)
advCount = len(advCat)
pronounCount = len(pronounCat)
prepositionCount = len(prepositionCat)
othersCount = len(othersCat)


plt.xticks(rotation='vertical')
plt.bar(["verb","noun","adjective","adverb","pronoun","preposition","others"], [verbCount,nounCount,adjCount,advCount,pronounCount,prepositionCount,othersCount])
plt.xlabel('POS')
plt.ylabel('Frequency')
plt.title('Histogram of POS')
plt.show()
plt.savefig("POSCount.png",format="png", dpi=1200)
