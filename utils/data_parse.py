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
import multiprocessing
import torch
import cite_update as cu
start_time = time.time()

spacy.require_gpu()

nlp = spacy.load("en_core_sci_scibert")

db = mc.connect()


# nlp.add_pipe('benepar', config={'model': 'benepar_en3'})

class DataParse:

    def getRef(self, data,refs):
        bibAuthor = data["content"]["annotations"]["bibauthor"]
        bibEntry = data["content"]["annotations"]["bibentry"]
        bibTitle = data["content"]["annotations"]["bibtitle"]
        bibVenue = data["content"]["annotations"]["bibvenue"]
        bibRef = data["content"]["annotations"]["bibref"]
        text = data["content"]["text"]
        refData = None
        bibs = []

        if all((bibRef, bibEntry, bibAuthor, bibTitle, bibVenue, text)):

            for ref in json.loads(bibRef):

                if ("attributes" in ref):

                    for entry in json.loads(bibEntry):

                        if ("attributes" in entry):

                            if (ref["attributes"]["ref_id"] == entry["attributes"]["id"]):
                                
                                refTitle = ""
                                refVenue = ""
                                authorList = []

                                for author in json.loads(bibAuthor):
                                    if int(author["start"]) >= int(entry["start"]) and int(author["start"]) <= int(entry["end"]):
                                        author = text[int(author["start"]):int(author["end"])].replace(",", "").strip()
                                        authorList.append(author.encode('utf-8').decode('unicode_escape'))

                                for venue in json.loads(bibVenue):
                                    if int(venue["start"]) >= int(entry["start"]) and int(venue["start"]) <= int(entry["end"]):
                                        refVenue = text[int(venue["start"]):int(venue["end"])].replace("}", "").encode('utf-8').decode('unicode_escape').strip()

                                for title in json.loads(bibTitle):
                                    if int(title["start"]) >= int(entry["start"]) and int(title["start"]) <= int(entry["end"]):
                                        refTitle = text[int(title["start"]):int(title["end"])].encode('utf-8').decode('unicode_escape').strip()
                                        for r in refs:
                                            if "title" in r["citedPaper"]:
                                                if r["citedPaper"]["title"].lower().strip() == refTitle.lower().strip():
                                                    refData = r["citedPaper"]

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
                                    
                else:
                    cite = text[int(ref["start"]):int(ref["end"])]

        return bibs

    def parse(self, data,db):
        # "bibref is the bib"
        text = data["content"]["text"]
        sentences = []
        paragraph = ""

        #  benepar.download('benepar_en3')
        if data["content"]["annotations"]["paragraph"] is not None:
            for i in json.loads(data["content"]["annotations"]["paragraph"]):
                paragraph += text[int(i["start"]): int(i["end"])].strip() + " "                
            try:
                doc = nlp(paragraph)
                for sentence in doc.sents:
                    # doc = nlp(sentence.text)
                    # if (list(doc.sents)[0]._.labels[0] == "S"):
                    if (len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric()):
                        sentences.append(sentence.text.strip())
                        

            except Exception as e:
                print(str(e))
                mc.save_record(db,"errors",{"error": str(e)})

        return sentences

    def prepareData(self, refs, sents, paperId):
        refDup = []
        nonCitedCount = 0
        cited = []
        nonCited = []

        for sent in sents:
            titleDup = []
            allRefs = []
            obj = {}

            for ref in refs:
                if ref["cite"] in sent and ref["cite"] not in refDup and ref["title"] not in titleDup:
                    titleDup.append(ref["title"])
                    refDup.append(ref["cite"])
                    allRefs.append(ref)

            obj["paperId"] = paperId
            obj["context"] = sent
            
            if len(allRefs) > 0:
                obj["ref"] = allRefs
                # mc.save_record(db, "citedData",obj)
                cited.append(obj)    
            else:
                nonCitedCount += 1
                if nonCitedCount <= 10:
                    # mc.save_record(db, "nonCitedData",obj)
                    nonCited.append(obj)
                    
        return {"cited":cited, "nonCited":nonCited}

    def getMetadata(self, data, apiData):
        combined_dict = {}
        authorlastnameList = []
        authorfirstnameList = []
        authorList = []
        titleText = ""
        venueText = ""

        # authorfirstname = data["content"]["annotations"]["authorfirstname"]
        # authorlastname = data["content"]["annotations"]["authorlastname"]
        abstract = data["content"]["annotations"]["abstract"]
        author = data["content"]["annotations"]["author"]
        title = data["content"]["annotations"]["title"]
        venue = data["content"]["annotations"]["venue"]
        text = data["content"]["text"]

        # abstractText = ""
        #
        # if abstract != "":
        #     abstractText = text[int(abstract[0]["start"]):int(abstract[0]["end"])].replace("A B S T R A C T",
        #                                                                                    "").replace("abstract",
        #                                                                                                "").replace(
        #         "Abstract", "").replace("ABSTRACT", "").strip()

        if all((abstract, title, venue, text, apiData)):
            if (abstract != "" and title != "" and venue != "" and text != ""):
                if all((apiData["fieldsOfStudy"], apiData["year"], apiData["publicationDate"], apiData["journal"], apiData["authors"])):
                    
                    for name in apiData["authors"]:
                        authorList.append(name["name"])
                    del apiData["authors"]
                    
                    # if authorlastname:
                    #     for lastname in json.loads(authorlastname):
                    #         authorlastnameList.append(
                    #             text[int(lastname["start"]):int(lastname["end"])].encode('utf-8').decode('unicode_escape'))

                    # if authorfirstname:
                    #     for firstname in json.loads(authorfirstname):
                    #         authorfirstnameList.append(
                    #             text[int(firstname["start"]):int(firstname["end"])].encode('utf-8').decode('unicode_escape'))

                    if title:
                        title = json.loads(title)[0]
                        titleText = text[int(title["start"]):int(title["end"])].encode('utf-8').decode('unicode_escape')

                    if venue:
                        venue = json.loads(venue)[0]
                        venueText = text[int(venue["start"]):int(venue["end"])].encode('utf-8').decode('unicode_escape')
                    

                    # if len(authorlastnameList) > 0 and len(authorfirstnameList) > 0:
                    #     for i, d in enumerate(authorfirstnameList):
                    #         author = authorfirstnameList[i] + " " + authorlastnameList[i]
                    #         author = author.encode('utf-8').decode('unicode_escape')
                    #         authorList.append(author)

                    obj1 = apiData

                    obj2 = {
                        "venue": venueText,
                        "title": titleText,
                        "author": authorList
                    }

                    combined_dict = obj1 | obj2

        return combined_dict
    
        
        
def process_batch(lines):
    api = APIRequest()
    dp = DataParse()

    for i,line in enumerate(lines):
        try:
            start = time.time()
            # Process each line    
            line = json.loads(line)
            
            text = line["content"]["text"]
            
            title = json.loads(line["content"]["annotations"]["title"])

            # titleText = text[int(title[0]["start"]):int(title[0]["end"])].encode('utf-8').decode('unicode_escape')
            # if titleText.lower() == "How digitalization reinvented entrepreneurial resilience during COVID-19".lower():    
        
            apiData = api.getData(line["content"]["source"]["pdfsha"])
            if "error" not in apiData:
                metadata = dp.getMetadata(line, apiData[0])
                if metadata:
                    objId = mc.save_record(db,"papers",metadata)
                    sents = dp.parse(line,db)
                        
                    if sents:
                        apiRef = api.getRefData(line["content"]["source"]["pdfsha"])["data"]
                        refs = dp.getRef(line,apiRef)
                            
                        if refs:
                            result = dp.prepareData(refs, sents, objId)
                                
                            # with open('debug.json', 'w', encoding='utf-8') as file:
                            #     file.write(json.dumps(result))
                            
                            c = cu.filterData(result["cited"])
                            print(c)

                                
                            mc.save_many(db,"citedData",result["cited"])
                            # mc.save_many(db,"nonCitedData",result["nonCited"])
                end = time.time()
                print(end - start)
                                
        except Exception as e:
            print(e)
            mc.save_record(db,"errors",{"error": str(e)})

def main():
    # multiprocessing.set_start_method('spawn')

    start_time = time.time()
    with open('../s2orc/data1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        process_batch(lines)
    end = time.time()
    # # print(end - start_time)
    # multiprocessing.set_start_method('spawn')
    # torch.cuda.synchronize()
    
    # batch_size = 100
    # processNum = multiprocessing.cpu_count()
    # # processNum = 2
    # print(multiprocessing.cpu_count())


    # with open('../s2orc/data2.txt', 'r', encoding='utf-8') as file:
    #      # Determine the number of available CPU cores

    #     # # Create a pool of worker processes

    #     # # Read the file in chunks and process each line in parallel
    #     # pool.imap(process_batch, file, chunksize=10000)
        
        
    #     lines = file.readlines()
    #     # process_batch(lines)
        

    #     with Pool(processes=processNum) as pool:
    #         for i in range(0, len(lines), batch_size):
    #             data = lines[i:i+batch_size]
    #             pool.map(process_batch, (data,))

    #         pool.close()
    #         pool.join()
    print(end - start_time)
    
if __name__ == "__main__":

    start_time = time.time()

    # # cu = CiteUpdate()
    
    # Define the batch size and number of worker processes
    batch_size = 100
    num_processes = 40

    # Find the total number of documents in the collection
    total_documents = mc.total_records(db,"citedData")
    # print(total_documents)
    # total_douments = 100
    # Calculate the number of batches based on the batch size
    
    num_batches = (total_documents // batch_size) + 1
    
    with open('../s2orc/data1.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Create a multiprocessing pool
    with Pool(processes=num_processes) as pool:
        for batch_number in range(num_batches):
            # Calculate the starting and ending indices for the current batch
            start_index = batch_number * batch_size
            end_index = start_index + batch_size
            db = mc.connect()

            # # Retrieve a batch of documents from the collection
            # records = mc.retrieve_records(db,"citedData",start_index,batch_size)
            

            pool.map(process_batch, (lines[start_index:end_index],))
         
                
            # Convert the documents to a list and process the batch in parallel
            
            
    print(time.time() - start_time)
