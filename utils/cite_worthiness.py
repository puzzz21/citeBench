import requests
import json
import nltk
import re
from thesis.cite_location import CiteLocation
from citation_parse import CitationParse
from context_length import ContextLength

class CiteWorthiness:

    # check if sentence and length
    def filterData(self,data):
        citedList = []
        cl = CiteLocation()
        cLen = ContextLength()

        for citing in data["cited"]:
            if len(citing["ref"]) == 1:
                cp = CitationParse()
                authors = citing["ref"][0]["authors"]
                print("ref: ", citing["ref"])

                parsedContext = cp.citationStyleRound(citing["context"])

                if parsedContext == None:
                    parsedContext = cp.citationStyleSquare(citing["context"])

                if parsedContext == None:
                    parsedContext = cp.citationStyleNoBracket(self, citing["context"], authors)
                #
                # if parsedContext == None:
                #     parsedContext = cp.citationStylePartial(self, citing["context"], authors, year)

                if parsedContext != None:

                    citationLen = cLen.getLength(parsedContext[0])

                    if(citationLen == "medium"):
                        contextObj = {
                            "context": parsedContext[0],
                            "isCited": True,
                            "citation": {
                                "citedTitle": citing["ref"][0]["title"],
                                #  "citedYear": data["metadata"]["year"],
                                "citedAuthor": authors,
                                "citation": parsedContext[1]
                            }
                        }

                        citedList.append(contextObj)

        for obj in data["nonCited"]:

            citationLen = cLen.getLength(obj["context"])
            context = obj["context"]

            if (citationLen == "medium"):
                pattern = r"[A-Za-z]{3,},"
                match = re.findall(pattern, context)

                if len(match) == 1:
                    match = re.search(pattern, context)
                    end_index = match.end()

                    context = context[:end_index - 1] + " <ref>" + context[end_index - 1:]

                else:
                    context = context[:len(context) - 1] + " <ref>" + context[len(context) - 1]

                contextObj = {
                            "context": context,
                            "isCited": False,
                            "citation": None
                }

                citedList.append(contextObj)

        return citedList

with open('all.json') as f:
    d = json.load(f)
cLen = ContextLength()
c = CiteWorthiness()

t = c.filterData(d["data"])
print(t)