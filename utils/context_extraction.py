import requests
import json
import nltk
import re
from data_parse import DataParse
import benepar, spacy
from spacy.tokenizer import Tokenizer

nlp = spacy.load("en_core_sci_scibert")

class ContextExtraction:

    def readData(self):
        with open('dump.txt') as f:
            d = json.load(f)
            return d

    def contextExtract(self,data,segment, num, direction):
        dp = DataParse()
        ref = dp.getRef(data)
        for cite in ref:
            cite = cite["cite"]
            citeSize = len(cite)
            ind = data["content"]["text"].index(cite)
            if(segment == "ch"):
                if(direction == "left"):
                    context = data["content"]["text"][ind - num: ind + citeSize]
                elif(direction == "right"):
                    context = data["content"]["text"][ind: ind + citeSize + num]
                else:
                    context = data["content"]["text"][ind - num : ind + citeSize + num]
            else:
                tokenCount = num//2
                if(direction == "left"):
                    text = data["content"]["text"][:ind]
                    tokens = text.split(" ")
                    context = " ".join(tokens[-tokenCount:]) + cite
                elif(direction == "right"):
                    text = data["content"]["text"][ind + citeSize:]
                    tokens = text.split(" ")
                    context = cite + " ".join(tokens[:tokenCount])
                else:
                    textRight = data["content"]["text"][ind + citeSize:]
                    tokensRight = textRight.split(" ")
                    textLeft = data["content"]["text"][:ind]
                    tokensLeft = textLeft.split(" ")
                    context = " ".join(tokensLeft[-tokenCount:])  + cite + " ".join(tokensRight[:tokenCount])
                    context = context.replace("\n","")

            print(context)
            print("------------------------")


c = ContextExtraction()
d = c.readData()

segment= "tk"
num = 20
direction = "bi"

c.contextExtract(d,segment,num,direction)






# with open('papers.json', 'w') as f:
#     json.dump.txt(response.json(), f)