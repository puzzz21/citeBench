import requests
import json
import nltk
import re
import spacy
import sys
sys.path.append("/home/pop533611/thesis")
import time

nlp = spacy.load("en_core_sci_scibert")
import mongoConnect as mc
from pymongo import MongoClient
from paper_parse import PaperParse
import cite_update as cu
import random
import threading
db = mc.connect()


class ContextLength:
    
    def process(self):
        start_time = time.time()
        threads = []

        for field in ["Computer Science","Medicine","Physics","Biology","Mathematics","Chemistry","Materials Science"]:
            thread = threading.Thread(target=self.filterYear, args=(field,))
            thread.start()
            threads.append(thread)
            
        for thread in threads:
            thread.join()               
                            
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Print the elapsed time
        print(f"Execution time: {elapsed_time} seconds")
            
    def filterYear(self,field):
        print("------------")
        print(field)
        yearFiltered = []
        
        for i in [(1996,2000),(2001,2005),(2006,2010),(2011,2015),(2016,2020)]:
            temp = self.createResult(field,i)
            yearFiltered.append(temp)
            
        json_data = json.dumps(yearFiltered)  # Convert data to a formatted JSON string

        with open(str(field) + ".json", "w") as json_file:
            json_file.write(json_data)     
            

    def createResult(self, field, i):
        pp = PaperParse()
        citedIds = []
        finalResult = []
        print("---")
        print(i)
                
        for j in range(10):
            print(j)    
            for idx, lenVal in enumerate(["short","medium","long"]):
                print("decided: ",lenVal)
                updated = 0
                            
                col = db["citedLen"]
                # Define the query criteria
                query = {
                                    'category': field,  # Ensure the 'medicine' field exists
                                    'year': {'$gte': i[0], '$lte': i[1]},  # Year between 1996 and 2000
                                    'group': j  # Group equal to 1
                    }

                # Find records that match the query criteria
                results = col.find(query)
                                
                for result in results:
                                
                    if result["corpusid"] not in citedIds:

                        citingTextCol = db["citingText"]
                        papers = citingTextCol.find({"citedPaperCId":result["corpusid"]})
                        papersList = list(papers)
                                    # json_result = json.dumps(papers, default=str)

                        for paper in papersList:
                                            
                                        # "bibref is the bib"
                            text = paper["content.text"]
                                                
                            bibs = pp.getRef(paper)                                    
                                                
                            entryRef = self.getEntryRef(paper, result["corpusid"])
                                                                                
                            sentences = self.getSentences(paper["content.annotations.paragraph"], text, entryRef)
                                        
                            citedSent = pp.prepareData(bibs, sentences, entryRef)
                            if len(citedSent) > 0 and len(citedSent[0]["ref"]) > 0:
                                dataset = self.getDataset(citedSent, result)
                                if dataset:
                                    if dataset[0]["lenClass"] == lenVal:
                                        context = dataset[0]["citedSent"]
                                        match = re.search("<REF>", context)
                                        if match:
                                            end_index = match.end()
                                            if (end_index + 1 == len(context)):
                                                print("found: ",dataset[0]["lenClass"] )
                                                obj = {"field":field, "year":i, "group":j,"citedPaper":result["corpusid"],"citingPaper":paper["citingCID"],"context":dataset}
                                                finalResult.append(obj)
                                                citedIds.append(result["corpusid"])
                                                updated = 1
                                                break
                                            
                    if updated == 1:
                        break
        
        return finalResult
                    

    def filterData(self):
        start_time = time.time()

        pp = PaperParse()
        
        citedIds = []
        for field in ["Computer Science","Medicine","Physics","Biology","Mathematics","Chemistry","Materials Science"]:
            print("------------")
            print(field)
            finalResult = []
            for i in [(1996,2000),(2001,2005),(2006,2010),(2011,2015),(2016,2020)]:
                print("---")
                print(i)
                
                for j in range(10):
                    print(j)
                     
                    for idx, lenVal in enumerate(["short","medium","long"]):
                        print(lenVal)
                        updated = 0
                            
                        col = db["citedLen"]
                        # Define the query criteria
                        query = {
                                    'category': field,  # Ensure the 'medicine' field exists
                                    'year': {'$gte': i[0], '$lte': i[1]},  # Year between 1996 and 2000
                                    'group': j  # Group equal to 1
                        }

                            # Find records that match the query criteria
                        results = col.find(query)
                            # docs = random.shuffle(list(col.find(query)))

                                
                        for result in results:
                                
                            if result["corpusid"] not in citedIds:

                                citingTextCol = db["citingText"]
                                papers = citingTextCol.find({"citedPaperCId":result["corpusid"]})
                                papersList = list(papers)
                                    # json_result = json.dumps(papers, default=str)

                                for paper in papersList:
                                            
                                        # "bibref is the bib"
                                    text = paper["content.text"]
                                                
                                    bibs = pp.getRef(paper)                                    
                                                
                                    entryRef = self.getEntryRef(paper, result["corpusid"])
                                                                                
                                    sentences = self.getSentences(paper["content.annotations.paragraph"], text, entryRef)
                                        
                                    citedSent = pp.prepareData(bibs, sentences, entryRef)
                                    if len(citedSent) > 0 and len(citedSent[0]["ref"]) > 0:
                                        dataset = self.getDataset(citedSent, result)
                                        if dataset:
                                            if dataset[0]["lenClass"] == lenVal:
                                                print("found: ",dataset[0]["lenClass"] )
                                                obj = {"field":field, "year":i, "group":j,"citedPaper":result["corpusid"],"citingPaper":paper["citingCID"],"context":dataset}
                                                finalResult.append(obj)
                                                citedIds.append(result["corpusid"])
                                                updated = 1
                                                break
                                            
                            if updated == 1:
                                break
                            
            json_data = json.dumps(finalResult)  # Convert data to a formatted JSON string

            with open(str(field )+ ".json", "w") as json_file:
                json_file.write(json_data)                    
                            
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Print the elapsed time
        print(f"Execution time: {elapsed_time} seconds")
        


    # if dataset:
                                    
            


        
    def getEntryRef(self,paper, citedCid):
        text = paper["content.text"]
        entryRef = None
        bibEntry = paper["content.annotations.bibentry"]
        bibRef = paper["content.annotations.bibref"]
        if bibEntry is not None and bibRef is not None:
            for entry in json.loads(bibEntry):
                if ( "matched_paper_id" in entry["attributes"]):
                    if (entry["attributes"]["matched_paper_id"] == citedCid):
                        bid = entry["attributes"]["id"]                                  
                        for ref in json.loads(bibRef):
                            # print(ref)
                            if "attributes" in ref:
                                if ref["attributes"]["ref_id"] == bid:
                                    refText = text[int(ref["start"]):int(ref["end"])]
                                    if refText != "":
                                        entryRef = refText
        return entryRef
    
    def getSentences(self,paragraph,text,entryRef):
        sentences = []
        paragraphRes = ""

        if paragraph is not None and entryRef is not None:
            for para in json.loads(paragraph):
                paragraphRes += text[int(para["start"]): int(para["end"])].strip() + " "                
            try:
                doc = nlp(paragraphRes)
                for sentence in doc.sents:
                    if (len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric()):
                        sent = sentence.text.strip()
                        sentences.append(sent)
            except Exception as e:
                print(str(e))
                mc.save_record(db,"errors",{"error": str(e)})
        return sentences
                    
    def getDataset(self,res,result):
        finalList = []

        for r in res:
            context = cu.filterSingleData(r ,result["year"])
            if (len(context) > 0):
                return context
            else:
                return None
            
    
c = ContextLength()
t = c.process()
print(json.dumps(t,ensure_ascii=False))
