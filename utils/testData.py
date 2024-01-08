import requests
import json
import nltk
import re
import benepar, spacy
from spacy.lang.en import English

nlp = spacy.load("en_core_web_lg")


class TestData:

    def readData(self):
        with open('res.json') as f:
            d = json.load(f)
            return d

    def test(self, data):
        x = []
        for d in data:
            if len(list(d["ref"])) > 0:
                x.append(d)
        return json.dumps(x)

c = TestData()


data = c.readData()
d = c.test(data)
print(d)


# with open('papers.json', 'w') as f:
#     json.dump.txt(response.json(), f)