import json
import re
import spacy
import sys
import time
import click

sys.path.append("/abyss/home/citation-recommendation/utils")
import mongoConnect as mc
from paper_parse import PaperParse
import cite_update as cu
from lenPatchIds import ids
import json
import pandas as pd
spacy.require_gpu()
nlp = spacy.load("en_core_sci_scibert")

dataClasses = {
    "length" : ["short", "medium", "long"],
    "position" : ["start", "middle", "end"],
    "intent" : ["background", "methodology", "result"],
    "worth" : ["comma","period"],
    "pos" : ["before_verb","before_noun","before_adjective","before_adverb","before_pronoun","before_preposition","before_others",
             "after_verb","after_noun","after_adjective","after_adverb","after_pronoun","after_preposition","after_others"],
    "low":[]
    
}

docName = {
    "intent": [
        "citedLenPatches",
        "citingLenPatches",
        "citingTextLenPatches",
        "finalIntentPatch8"
    ],
    "position": [
        "citedLocPatches",
        "citingLocPatches",
        "citingTextLocPatches",
        "finalLocationsPatches8"
    ],
    "worth": [
        "citedWorthNew",
        "citingWorthNew",
        "citingTextWorthNew",
        "finalWorthsss"
    ],
    "length": [
         "citedLength",
        "citingLength",
        "citingTextLength",
        "lengthPatch"
    ],
    "pos": [
        "citedLenPatches2",
        "citingLenPatches2",
        "citingTextLenPatches2",
        "finalPosWordsPatch1"
    ],
    "low": [
        "citedLow",
        "citingLow",
        "citingTextLow",
        "finalLow"
    ]
}

patchFile = {
    "length": "missinglength.json",
    "position": "missingposition.json",
    "intent": "missingintent.json",
    "pos": "missingpos.json"
}
# @click.command()
# @click.option("--datasetname", required=True, type=click.Choice(['length', 'position', 'intent',"worth"]), 
#               help="Name of the dataset. Pick among length, position, and intent")

def process():
    dg = DataGeneration("length")
    dg.run()

class DataGeneration:
    def __init__(self, datasetname):
        self.datasetname = datasetname
    
    def run(self):

        with open(patchFile[self.datasetname]) as f:
            d = json.load(f)
            
        df = pd.DataFrame.from_dict(pd.json_normalize(d), orient='columns')

        for index, row in df.iterrows():
            dupIds = []
            query = {
                    'category': row["field"],
                    'year': {'$gte': row["year"][0], '$lte': row["year"][1]},
                    'group': row["group"]
            }

            updated = 0

        #     # Find records that match the query criteria
            pp = PaperParse()
            results = mc.get_records(docName[self.datasetname][0], query)
                
        #     # Loop through matching results
            for result in results:
                if result["corpusid"] not in ids and result["corpusid"] not in dupIds:
                    print("hi")
                    papers = mc.get_records(docName[self.datasetname][2],{"citedPaperCId": result["corpusid"]})
                    papersList = list(papers)

                    # Loop through papers
                    for paper in papersList:
                        print("paper::::")
                        text = paper["content.text"]
                        
                        bibs = pp.getRef(paper)
                        if bibs is not None:
                            entryRef = self.getEntryRef(paper, result["corpusid"])
                            if entryRef is None:
                                continue
                            # paragraph, text, entryRef, classWorth,bibs,result
                            sentences = self.getSentences(paper["content.annotations.paragraph"], text, entryRef)
                            if len(sentences) == 0:
                                continue
                                
                            citedSent = pp.prepareData(bibs, sentences, self.datasetname)
                            print("citedSent: ",citedSent)
                                
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
                                dataset = self.getDataset(citedSent, result, self.datasetname, paper["citingCID"])
                                if dataset and self.datasetname + "Class" in dataset[0]:
                                    print(dataset[0]["lengthClass"] , "::::: ", row["class"])

                                    posCond = dataset[0]["positionClass"] == "end"
                                    lenCond = dataset[0]["lengthClass"] == "medium"
                                    posDataFilter = self.datasetname == "position" and lenCond and dataset[0]["positionClass"] == row["class"]
                                    # classCond = dataset[0][self.datasetname + "Class"] == lenVal
                                    lenDataFilter = self.datasetname == "length" and posCond and dataset[0]["lengthClass"] == row["class"]
                                    print("lenDataFilter: ", lenDataFilter)
                                    
                                    intentDataFilter = self.datasetname == "intent" and lenCond and dataset[0]["intentClass"] == row["class"]
                                    psDataFilter = self.datasetname == "pos" and dataset[0]["positionClass"] == "middle" and lenCond and row["class"] in  dataset[0]["posClass"]

                                    if intentDataFilter or lenDataFilter or posDataFilter:
                                        obj = {
                                                    "field": row["field"],
                                                    "year": row["year"],
                                                    "group": row["group"],
                                                    "citedPaper": result["corpusid"],
                                                    "citingPaper": paper["citingCID"],
                                                    "context": dataset
                                        }
                                        mc.insert_record(docName[self.datasetname][3],obj)
                                        updated = 1
                                        break
                                    
                                    elif psDataFilter:
                                        dupIds.append(result["corpusid"])
                                        obj = {
                                                    "field": row["field"],
                                                    "year": row["year"],
                                                    "group": row["group"],
                                                    "citedPaper": result["corpusid"],
                                                    "citingPaper": paper["citingCID"],
                                                    "context": dataset,
                                                    "selectedPOSClass" : row["class"]  
                                        }
                                        mc.insert_record(docName[self.datasetname][3],obj)
                                        updated = 1
                                        break
                    if updated == 1:
                        break
                                        

                                        

        
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
                    if isinstance(entry["attributes"]["matched_paper_id"], str):
                        entry["attributes"]["matched_paper_id"] = entry["attributes"]["matched_paper_id"].strip()
                        
                    if isinstance(citedCid,str):
                        citedCid = citedCid.strip()

                      
                    # Check if the matched_paper_id matches the citedCid
                    if int(entry["attributes"]["matched_paper_id"]) == int(citedCid):                        
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

    def getSentences(self, paragraph, text, entryRef):
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
            if entryRef in paragraphRes:
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
    

    def getDataset(self, records, result, citingDataset, citingCID):
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
                    citingPapers = mc.get_records(docName[self.datasetname][1], {"citedPaperCId": result["corpusid"], "citingCID":citingCID })
                    for paper in citingPapers:
                        intent = paper["meta"]["intents"]
                        if len(intent) == 1:
                            context[0]["intentClass"] = intent[0].lower()

                return context
 
        # Return None if no valid context is found
        return None
            
if __name__ == "__main__":
    process()
