import requests
import json
import nltk
import re
from citation_parse import CitationParse
import spacy

nlp = spacy.load("en_core_sci_scibert")

class ContextLength:

    def filterData(self,data):
        contextList = []
        year = data["metadata"]["year"]

        # loop through the citing papers
        for citing in data["data"]["cited"]:
            if len(citing["ref"]) == 1:

                authors = citing["ref"][0]["authors"]

                cp = CitationParse()

                parsedContext = cp.citationStyleRound(citing["context"])

                if parsedContext == None:
                    parsedContext = cp.citationStyleSquare(citing["context"])

                if parsedContext != None:
                    contextObj = {
                        "context": parsedContext[0],
                        "location": self.getLength(parsedContext[0]),
                        "citation": {
                            "citedTitle": citing["ref"][0]["title"],
                            #  "citedYear": data["metadata"]["year"],
                            "citedAuthor": authors,
                            "citation": parsedContext[1]
                        }
                    }

                    contextList.append(contextObj)

        return contextList


    def getLength(self, context):
        new_con = context.replace("<REF>","")
        doc = nlp(new_con)

        filtered_text = []
        for token in doc:
            if not token.is_punct:
                filtered_text.append(token.text)

        # Get length of the context
        wordsLen = len(new_con.split())
        wordsLen = len(filtered_text)

        if wordsLen <= 13:
            return "short"
        elif wordsLen > 13 and wordsLen <= 25:
            return "medium"
        else:
            return "long"

with open('all.json') as f:
    d = json.load(f)

c = ContextLength()
t = c.filterData(d)
print(json.dumps(t,ensure_ascii=False))
