import requests
import json
import nltk
import re
from utils import Utils
from citation_parse import CitationParse

class CiteLocation:

    def filterData(self,data):
        print(data)
        contextList = []

        #loop through the citing papers
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
                                    "location": self.getPosition(parsedContext[0]),
                                    "citation": {
                                        "citedTitle": citing["ref"][0]["title"],
                                      #  "citedYear": data["metadata"]["year"],
                                        "citedAuthor": authors,
                                        "citation": parsedContext[1]
                                    }
                                }

                    contextList.append(contextObj)
        return contextList

    def getPosition(self,context):
        position = ""
        match = re.search("<REF>", context)
        if match:
            start_index = match.start()
            end_index = match.end()

            if (end_index + 1 == len(context)):
                position = "last"
            elif (start_index == 0):
                position = "first"
            else:
                position = "middle"

        return position

with open('all.json') as f:
    d = json.load(f)

c = CiteLocation()
t = c.filterData(d)
print(json.dumps(t,ensure_ascii=False))