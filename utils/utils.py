import requests
import benepar, spacy
import json
import nltk
import re
import chardet
from API_request import APIRequest

nlp = spacy.load("en_core_sci_scibert")


class Utils:

    def getSentences(self, data):
        x = ""
        print(data["content"])
        text = data["content"]["text"]

        #  benepar.download('benepar_en3')

        for i in json.loads(data["content"]["annotations"]["paragraph"]):
            x += text[int(i["start"]): int(i["end"])].strip() + " "

        doc = nlp(x)
        sentences = []

        nlp.add_pipe('benepar', config={'model': 'benepar_en3'})
        for x in doc.sents:
            doc = nlp(x.text)
            if (list(doc.sents)[0]._.labels[0] == "S"):
                if (doc.text.strip()[-1] in [".", "!", "?"] and not doc.text.strip()[0].isnumeric()):
                    sentences.append(doc.text.strip())

        return sentences


