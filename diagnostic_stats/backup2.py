import json
import re
import spacy
import sys
import time
import click

sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc
from paper_parse import PaperParse
import cite_update as cu
import multiprocessing
from citedList import allCitedIds


nlp = spacy.load("en_core_sci_scibert")

dataClasses = {
    "length" : ["short", "medium", "long"],
    "position" : ["start", "middle", "end"],
    "intent" : ["background", "methodology", "result"],
    "worth" : ["comma","period"]
}

docName = {
    "intent": ["citedType","citingType","citingTextType","finalType"],
    "position":["citedLoc","citingLoc","citingTextLoc","finalLocation"],
    "worth":["citedWorth","citingWorth","citingTextWorth","finalWorth"],
    "length":["citedLen","citingLen","citingText","finalLen"]

}

# @click.command()
# @click.option("--datasetname", required=True, type=click.Choice(['length', 'position', 'intent',"worth"]), 
#               help="Name of the dataset. Pick among length, position, and intent")

def process():
    datasetname = "position"
    dg = DataGeneration(datasetname)
    dg.run()

class DataGeneration:
    def __init__(self, datasetname):
        self.datasetname = datasetname
    
    def run(self):
        """
            Processes Dataset for each fields in the multiprocesses, parallely
        """
        
        start_time = time.time()
        # List of fields
        fields = ["Biology","Chemistry","Computer Science","Materials Science","Medicine","Physics", "Mathematics"]

        for field in fields:
            self.filterYear(field)
            
        # # Create a pool of processes
        # pool = multiprocessing.Pool(processes=len(fields))

        # # Map the process_field function to the list of fields
        # pool.map(self.filterYear, fields)

        # # Close the pool and wait for all processes to finish
        # pool.close()
        # pool.join()         
                            
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Print the elapsed time
        print(f"Execution time: {elapsed_time} seconds")
            
    def filterYear(self, field):
        """
            Processes Dataset for each fields and loop through the years to filter data based in the specified years
        """
        
        print("------------")
        print(field)
        # yearFiltered = []
        # (1996,2000),(2001,2005),
        for i in [(1996,2000),(2001,2005),(2006,2010),(2011,2015),(2016,2020)]:
            temp = self.createResult(field,i)
            # yearFiltered.append(temp)
            
        # json_data = json.dumps(yearFiltered)
            
        # fileFileName = field.replace(" ","")
        # with open(f"{self.datasetname}_{fileFileName}.json", "w") as json_file:
        #     json_file.write(json_data)     
            

    def createResult(self, field, year):
        """
            Retrieves the papers of the specified fields, year and parse the papers and get the result based on the specified datasetname
        """
        # Initialize necessary objects
        pp = PaperParse()
        citedIds = set()
        finalResult = []
        classes = dataClasses[self.datasetname]

        # Debugging information
        print("---")
        print(year)

        # Loop over groups (0-9)
        for group in range(10):
            # Debugging information
            print(group)
            
            # Loop over length values
            for lenVal in classes:
                # Debugging information
                print("decided: ", lenVal)
                
                # Flag to track if we've updated
                updated = 0

                # Define the query criteria
                query = {
                    'category': field,
                    'year': {'$gte': year[0], '$lte': year[1]},
                    'group': group
                }

                # Find records that match the query criteria
                results = mc.get_records(docName[self.datasetname][0], query)
                # Loop through matching results
                for result in results:
                    if result["corpusid"] not in citedIds and result["corpusid"] not in allCitedIds:
                        papers = mc.get_records(docName[self.datasetname][2], {"citedPaperCId": result["corpusid"]})
                        papersList = list(papers)

                        # Loop through papers
                        for paper in papersList:
                            text = paper["content.text"]
                            
                            

                            bibs = pp.getRef(paper)
                            
                            if bibs is not None:
                                entryRef = self.getEntryRef(paper, result["corpusid"])
                                if entryRef is None:
                                    continue
                                # paragraph, text, entryRef, classWorth,bibs,result
                                sentences = self.getSentences(paper["content.annotations.paragraph"], text, entryRef, lenVal ,bibs, result)
                                if len(sentences) == 0:
                                    continue
                                
                                citedSent = pp.prepareData(bibs, sentences, self.datasetname)
                                
                                # if self.datasetname == "worth":
                                #     print(sentences)
                                    
                                    # if dataObj and self.datasetname + "Class" in dataObj[0]:
                                    #     posCond = dataObj[0]["lengthClass"] == "medium"
                                    #     if dataObj[0][self.datasetname + "Class"] == lenVal and posCond:
                                    #         # print("dataObj: ", dataObj)
                                    #         print("found: ", dataset[0][self.datasetname + "Class"])
                                    #         print(notCitedSentences)
                                            
                                            # sentences = self.getSentences(paper["content.annotations.paragraph"], text, None,lenVal)
                                            
                                            
                                
                                if len(citedSent) > 0 and len(citedSent[0]["ref"]) > 0:
                                    dataset = self.getDataset(citedSent, result, self.datasetname)
                                    if dataset and self.datasetname + "Class" in dataset[0]:
                                        
                                        posCond = dataset[0]["positionClass"] == "end"
                                        lenCond = dataset[0]["lengthClass"] == "medium"
                                        classCond = dataset[0][self.datasetname + "Class"] == lenVal
                                        lenDataFilter = self.datasetname == "length" and classCond and posCond
                                        posDataFilter = self.datasetname == "position" and classCond and lenCond
                                        psDataFilter = self.datasetname == "pos" and classCond and posCond and lenCond
                                        intentDataFilter = self.datasetname == "intent" and classCond and lenCond and posCond
                                        worthDataFilter = self.datasetname == "worth" and classCond and lenCond
                                        
                                        if lenDataFilter or posDataFilter or intentDataFilter or worthDataFilter:
                                            # Debugging information
                                            print("found: ", dataset[0][self.datasetname + "Class"])
                                            
                                            # Create result object
                                            obj = {
                                                "field": field,
                                                "year": year,
                                                "group": group,
                                                "citedPaper": result["corpusid"],
                                                "citingPaper": paper["citingCID"],
                                                "context": dataset
                                            }
                                            
                                            if worthDataFilter:
                                                notCitedSentence = self.nonCitedSentences(paper["content.annotations.paragraph"], text, lenVal,bibs)
                                                if notCitedSentence is None:
                                                    continue
                                                notCitedObj = {
                                                    "field": field,
                                                    "year": year,
                                                    "group": group,
                                                    "citingPaper": paper["citingCID"],
                                                    "context": notCitedSentence
                                                }
                                                # try:
                                                #     lang1 = detect(notCitedSentence)
                                                #     lang2 = detect(dataset)
                                                #     if lang1 != 'en' and lang2 != 'en':
                                                #         continue
                                                # except Exception as e:
                                                #     print(f"An unexpected error occurred: {e}")
                                                #     continue

                                                worthObj = { "class": lenVal, "data" : {"cited":obj, "notCited":notCitedObj}}
                                                finalResult.append(worthObj)
                                                mc.insert_record(docName[self.datasetname][3],worthObj)
                                            else:
                                                finalResult.append(obj)
                                                mc.insert_record(docName[self.datasetname][3],obj)
                                           
                                            
                                            
                                            # Add cited ID to the set
                                            citedIds.add(result["corpusid"])
                                            updated = 1
                                            break
                        if updated == 1:
                            break
            print("finalResult :",finalResult)  
                        
        return finalResult

        
    def getEntryRef(self, paper, citedCid):
        """
            Search the cited paper's entry reference in the citing paper's context.
        """
        # Extract necessary data from the paper object
        text = paper["content.text"]
        bibEntry = paper["content.annotations.bibentry"]
        bibRef = paper["content.annotations.bibref"]
        
        # Initialize the entryRef variable
        entryRef = None

        # Check if both bibEntry and bibRef are present
        if bibEntry is not None and bibRef is not None:
            # Convert the JSON-encoded bibEntry to a list of dictionaries
            entries = json.loads(bibEntry)
            
            # Iterate through each entry
            for entry in entries:
                if "matched_paper_id" in entry["attributes"]:
                    # Check if the matched_paper_id matches the citedCid
                    if entry["attributes"]["matched_paper_id"] == citedCid:
                        bid = entry["attributes"]["id"]
                        
                        # Convert the JSON-encoded bibRef to a list of dictionaries
                        refs = json.loads(bibRef)
                        
                        # Iterate through each reference
                        for ref in refs:
                            if "attributes" in ref:
                                # Check if the ref_id matches the bid
                                if ref["attributes"]["ref_id"] == bid:
                                    # Extract the reference text from the paper's text
                                    refText = text[int(ref["start"]):int(ref["end"])]
                                    
                                    # Check if the extracted reference text is not empty
                                    if refText != "":
                                        entryRef = refText
                                        break  # Stop searching if a valid entryRef is found
        return entryRef

    def getSentences(self, paragraph, text, entryRef, classWorth,bibs,result):
        """
            Parse the text to sentences
        """
        citedSentences = []
        paragraphRes = ""
        
        # Check if paragraph and entryRef are not None
        if paragraph is not None:
            
            # Iterate through each paragraph in the JSON-encoded paragraph
            for para in json.loads(paragraph):
                # Concatenate the text within the paragraph
                paragraphRes += text[int(para["start"]):int(para["end"])].strip() + " "

        try:
            # Process the concatenated paragraph using spaCy
            doc = nlp(paragraphRes)

            # Iterate through sentences in the processed paragraph
            for sentence in doc.sents:
                # Check sentence criteria (length, punctuation, not starting with a number)
                if len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric():
                    sent = sentence.text.strip()
                    if entryRef:
                        if entryRef in sent:
                            citedSentences.append(sent)
                                
        except Exception as e:
            # Handle exceptions and log them (you may adapt the logging mechanism)
            print(str(e))
            mc.get_records("errors", {"error": str(e)})
        
        return citedSentences
    
    
    def nonCitedSentences(self, paragraph, text, classWorth,bibs):
        """
            Parse the text to sentences
        """
        notCited = None
        paragraphRes = ""
        
        # Check if paragraph and entryRef are not None
        if paragraph is not None:
            
            # Iterate through each paragraph in the JSON-encoded paragraph
            for para in json.loads(paragraph):
                # Concatenate the text within the paragraph
                paragraphRes += text[int(para["start"]):int(para["end"])].strip() + " "

        try:
            # Process the concatenated paragraph using spaCy
            doc = nlp(paragraphRes)

            # Iterate through sentences in the processed paragraph
            for sentence in doc.sents:
                # Check sentence criteria (length, punctuation, not starting with a number)
                if len(sentence.text) > 3 and sentence.text.strip()[-1] in [".", "!", "?"] and not sentence.text.strip()[0].isnumeric():
                    sent = sentence.text.strip()
                        # dataObj = self.getDataset(sent, result, self.datasetname)
                    context = cu.filterSingleData(sent, None)
                    if context[0]["worthClass"] == classWorth and context[0]["lengthClass"] == "medium":
                                    
                        citedSent = context[0]["citedSent"]
                        good = True
                        for bib in bibs:
                            if bib["cite"] in citedSent:
                                good = False
                                break                                    
                        if good:
                            notCited = citedSent                                

                                
        except Exception as e:
            # Handle exceptions and log them (you may adapt the logging mechanism)
            print(str(e))
            mc.get_records("errors", {"error": str(e)})
        
        return notCited
    

    def getDataset(self, records, result, citingDataset):
        r = []
        """
            Retrieve correctly cited sentences by matching with various citation styles and return the metadata on the citation 
        """
        for record in records:
            # Filter the data for a single context
            context = cu.filterSingleData(record, result["year"])
            r.append(context)
            # Check if there's a valid context to retrieve the intent class for intent dataset
            if len(context) > 0:
                if citingDataset == "intent": 
                    citingPapers = mc.get_records(docName[self.datasetname][1], {"citedPaperCId": result["corpusid"]})
                    for paper in citingPapers:
                        intent = paper["meta"]["intents"]
                        if len(intent) == 1:
                            context[0]["intentClass"] = intent[0].lower()
                return context

            
            
        
        # Return None if no valid context is found
        return None
            
if __name__ == "__main__":
    process()
