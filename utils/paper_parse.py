import requests
import benepar, spacy
import json
import nltk
import re
import chardet
from API_request import APIRequest
import mongoConnect as mc
import time
from multiprocessing import Pool
import torch
import cite_update as cu
start_time = time.time()


db = mc.connect()


# nlp.add_pipe('benepar', config={'model': 'benepar_en3'})

class PaperParse:

    def getRef(self, data):
        bibAuthor = data["content.annotations.bibauthor"]
        bibEntry = data["content.annotations.bibentry"]
        bibTitle = data["content.annotations.bibtitle"]
        bibVenue = data["content.annotations.bibvenue"]
        bibRef = data["content.annotations.bibref"]
        text = data["content.text"]
        refData = None
        bibs = []
        
        abstract = data["content.annotations.abstract"]
        author = data["content.annotations.author"]
        title = data["content.annotations.title"]
        venue = data["content.annotations.venue"]

        if all((abstract, title, venue, text, author)) and (abstract != "" and title != "" and venue != "" and text != "" and author != ""):     
                           
# if all((apiData["fieldsOfStudy"], apiData["year"], apiData["publicationDate"], apiData["journal"], apiData["authors"])):
                    
            if all((bibRef, bibEntry, bibAuthor, bibTitle, bibVenue)):

                for ref in json.loads(bibRef):

                    if ("attributes" in ref):

                        for entry in json.loads(bibEntry):

                            if ("attributes" in entry):

                                if (ref["attributes"]["ref_id"] == entry["attributes"]["id"]):
                                    
                                    refTitle = ""
                                    refVenue = ""
                                    authorList = []
                                    
                                    try:
                                    
                                        for author in json.loads(bibAuthor):
                                            if int(author["start"]) >= int(entry["start"]) and int(author["start"]) <= int(entry["end"]):
                                                author = text[int(author["start"]):int(author["end"])].replace(",", "").replace("\\N", "N").strip()
                                                authorList.append(author.encode('utf-8').decode('unicode-escape'))

                                        for venue in json.loads(bibVenue):
                                            if int(venue["start"]) >= int(entry["start"]) and int(venue["start"]) <= int(entry["end"]):
                                                refVenue = text[int(venue["start"]):int(venue["end"])].replace("}", "").replace("\\N", "N").rstrip('\\').encode('utf-8').decode('unicode-escape').strip()
                                                
                                        for title in json.loads(bibTitle):
                                            if int(title["start"]) >= int(entry["start"]) and int(title["start"]) <= int(entry["end"]):
                                                refTitle = text[int(title["start"]):int(title["end"])].replace("\\N", "N").rstrip('\\').encode('utf-8').decode('unicode-escape').strip()                                 
                                    
                                    except Exception as e:
                                        print(f"An exception occurred: {e}")
                                        return None
                                        
                                    cite = text[int(ref["start"]):int(ref["end"])]
                                        
                                    if len(authorList) > 0 and refTitle != "" and refVenue != "":
                                        obj = {
                                                "cite": cite,
                                                "citation": text[int(entry["start"]):int(entry["end"])],
                                                "authors": authorList,
                                                "title": refTitle,
                                                "venue": refVenue
                                        }

                                        if refData:
                                            obj = obj | refData
                                        bibs.append(obj) 

        with open('bibs.json', 'w') as f:
            json.dump(bibs, f)
        return bibs

    # def parse(self, data,db):
    #     # "bibref is the bib"
    #     text = data["content.text"]
    #     sentences = []
    #     paragraph = ""

    #     if data["content.annotations.paragraph"] is not None:
            
    #         for para in json.loads(data["content.annotations.paragraph"]):
    #             paragraph += text[int(para["start"]): int(para["end"])].strip() + " "                
    #         try:
    #             doc = nlp(paragraph)
    #             for sentence in doc.sents:
    #                 # doc = nlp(sentence.text)
    #                 # if (list(doc.sents)[0]._.labels[0] == "S"):
    #                 if (len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric()):
    #                     sentences.append(sentence.text.strip())
                        

    #         except Exception as e:
    #             print(str(e))
    #             mc.save_record(db,"errors",{"error": str(e)})

    #     return sentences

    def prepareData(self, refs, sents, entryRef):
        refDup = []
        cited = []
        notCited = []
        allNotCited = 0
        # print("sents len: ", len(sents))
        for sent in sents:
            titleDup = []
            allRefs = []
            obj = {}

            for ref in refs:
                if ref["cite"] in sent and ref["cite"] not in refDup and ref["title"] not in titleDup:
                    titleDup.append(ref["title"])
                    refDup.append(ref["cite"])
                    allRefs.append(ref)
            
            obj["context"] = sent
            
            if len(allRefs) == 1:
                if (allRefs[0]["cite"] in sent):
                    obj["ref"] = allRefs
                    obj["worth"] = "cited"
                    cited.append(obj)
                    
                    # mc.save_record(db, "citedData",obj)
                       
            # elif len(allRef) == 0:
                # allNotCited += 1
                # if allNotCited < 1:

                
            
                    

            #     # get length
            #     citationLen = cLen.getLength(sent)
                

            #     if (citationLen == "medium"):
            #         pattern = r"[A-Za-z]{3,},"
            #         match = re.findall(pattern, sent)

            #         if len(match) == 1:
            #             match = re.search(pattern, sent)
            #             end_index = match.end()

            #             context = context[:end_index - 1] + " <ref>" + context[end_index - 1:]

            #         else:
            #             context = context[:len(context) - 1] + " <ref>" + context[len(context) - 1]
                        
            #     nonCited.append(sent)
                
        return cited
    
    def getMetadata(self, data, apiData):
        combined_dict = {}
        authorlastnameList = []
        authorfirstnameList = []
        authorList = []
        titleText = ""
        venueText = ""

        abstract = data["content.annotations.abstract"]
        author = data["content.annotations.author"]
        title = data["content.annotations.title"]
        venue = data["content.annotations.venue"]
        text = data["content.text"]


        if all((abstract, title, venue, text, apiData)):
            if (abstract != "" and title != "" and venue != "" and text != ""):
                if all((apiData["fieldsOfStudy"], apiData["year"], apiData["publicationDate"], apiData["journal"], apiData["authors"])):
                    
                    for name in apiData["authors"]:
                        authorList.append(name["name"])
                    del apiData["authors"]
                    
                    if title:
                        title = json.loads(title)[0]
                        titleText = text[int(title["start"]):int(title["end"])].encode('utf-8').decode('unicode_escape')

                    if venue:
                        venue = json.loads(venue)[0]
                        venueText = text[int(venue["start"]):int(venue["end"])].encode('utf-8').decode('unicode_escape')
                    

                    obj1 = apiData

                    obj2 = {
                        "venue": venueText,
                        "title": titleText,
                        "author": authorList
                    }

                    combined_dict = obj1 | obj2

        return combined_dict
    
        
        
    # def process():
    #     api = APIRequest()

    #     for i,line in df.iterrows():
    #         try:
    #             start = time.time()
    #     #         # Process each line    
                
    #             text = line["content.text"]
                
    #             title = json.loads(line["content.annotations.title"])

            
    #             apiData = api.getData(line["content.source.pdfsha"])
    #             if "error" not in apiData:
    #                 metadata = self.getMetadata(line, apiData[0])
    #                 if metadata:
    #                     # objId = mc.save_record(db,"lenPapaers")
    #                     sents = self.parse(line,db)
                            
    #                     if sents:
    #                         apiRef = api.getRefData(line["content.source.pdfsha"])["data"]
    #                         refs = self.getRef(line,apiRef)
                                
    #                         if refs:
    #                             result = self.prepareData(refs, sents, objId)
                                    
    #                             c = cu.filterData(result["cited"])

                                    
    #                             # mc.save_many(db,"locCitedData",result["cited"])
    #                             # mc.save_many(db,"nonCitedData",result["nonCited"])
    #                 end = time.time()
    #                 print(end - start)
                                    
    #         except Exception as e:
    #             print(e)
    #             # mc.save_record(db,"errors",{"error": str(e)})
                
