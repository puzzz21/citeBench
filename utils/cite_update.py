from API_request import APIRequest
import mongoConnect as mc
import time
from citation_parse import CitationParse
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import string
# nltk.download('averaged_perceptron_tagger')


# class CiteUpdate:
def filterData(data):
    contextList = []

    #loop through the citing papers
    for i,citing in enumerate(data):


        if len(citing["ref"]) == 1:
            
            ref = citing["ref"][0]
            cp = CitationParse()
                                
            styles = [
                    cp.citationStyleRound,
                    cp.citationStyleSquare,
                    cp.citationStyleNoBracket,
                    cp.citationStylePartial,
                    cp.citationStyleCase,
                    cp.citationStyleSuperScript,
                    cp.citationStyleVancouver
            ]

            parsedContext = None
            if "year" in ref:
                for style in styles:
                    parsedContext = style(citing["context"], ref["authors"], ref["year"])
                    if parsedContext is not None:
                        break
                    elif parsedContext == "many":
                        parsedContext = None
                        break
                    
            if parsedContext:
                
                sent = parsedContext[0]                
                     
                if "<REF>" in sent:

                    pPattern = f"((p\.|pp\.) \d+(?:-\d+)?)"
                    matches1 = re.search(pPattern, sent)
                    
                    if matches1:
                        start_index = matches1.start()
                        end_index = matches1.end()
                        sent = sent[:start_index] + "" + sent[end_index:]

                    words = nltk.word_tokenize(sent)
                    
                    wordList = [word for word in words if word not in string.punctuation]
                    pos_tags = nltk.pos_tag(wordList)
 
                    totalRef = wordList.count("REF")
                                        
                    if totalRef == 1:
                        
                        tokenLen = len(wordList)
                    
                        citeLoc = wordList.index("REF")
                                                
                        POSWordBefore = pos_tags[citeLoc - 1][1]
                        POSWordAfter = pos_tags[citeLoc + 1][1]
                        pos = None
                        
                        # if POSWordBefore == "NNP" or POSWordBefore == "NNPs":
                        #     pos = "noun"
                        # elif POSWordBefore == "IN":
                        #     pos = "preposition"
                        # elif POSWordBefore == "VBN" or POSWordBefore == "VBP" or POSWordBefore == "VBZ":
                        #     pos = "verb"
                        
                        if citeLoc <=4:
                            loc = "start"
                        elif citeLoc >= len(wordList) - 1:
                            loc = "end"
                        else:
                            loc = "intermediary"
                                                    
                        obj = {
                            "tokenLen" : tokenLen,
                            "citeLocation": citeLoc,
                            "POSWordBefore":POSWordBefore,
                            "POSWordAfter":POSWordAfter,
                            "citedSent": parsedContext[0],
                            "citedText": parsedContext[1],
                        }
                        citing["citeInfo"] = obj
                        ob = { "$set": { "citeInfo": obj } }
                        # mc.update(db, "citedData", {"_id": citing["_id"]}, ob)
                        contextList.append(obj)
                        

            
            # for token in splitContext:
            #     if not token.is_punct:
            #         filteredText.append(token)
                    
            # print(filteredText)
                    
            # filtered_text.append(token.text)

            # # Get length of the context
            # wordsLen = len(new_con.split())
                    
            # if parsedContext:
            #     obj = {
            #         "parsedContext": parsedContext[0],
            #         "citedText": parsedContext[1],
            #         "tokenLen": len(parsedContext[0].split(" "))
            #     }
    
    return contextList


# class CiteUpdate:
def filterSingleData(citing,year):
    contextList = []
    # and citing["ref"] is not 0
    if "ref" in citing:
        #loop through the citing papers
        cp = CitationParse()
                                    
        styles = [
                        cp.citationStyleRound,
                        cp.citationStyleSquare,
                        cp.citationStyleNoBracket,
                        cp.citationStylePartial,
                        cp.citationStyleCase,
                        cp.citationStyleSuperScript,
                        cp.citationStyleVancouver
            ]

        parsedContext = None
        for style in styles:
            parsedContext = style(citing["context"], citing["ref"][0]["authors"],str(year))
            if parsedContext is not None:
                break
            elif parsedContext == "many":
                parsedContext = None
                break
        
                
        if parsedContext:
                    
            sent = parsedContext[0]                
                        
            if "<REF>" in sent:

                pPattern = f"((p\.|pp\.) \d+(?:-\d+)?)"
                matches1 = re.search(pPattern, sent)
                        
                if matches1:
                    start_index = matches1.start()
                    end_index = matches1.end()
                    sent = sent[:start_index] + "" + sent[end_index:]

                words = nltk.word_tokenize(sent)
                        
                wordList = [word for word in words if word not in string.punctuation]
                pos_tags = nltk.pos_tag(wordList)
    
                totalRef = wordList.count("REF")
                                            
                if totalRef == 1:
                            
                    tokenLen = len(wordList)
                    
                    citeLoc = wordList.index("REF")  
                    
                    loc = None
                    
                    if citeLoc <=4:
                        loc = "start"
                    elif citeLoc >= len(wordList) - 1:
                        loc = "end"
                    else:
                        loc = "middle" 
                        
                    if tokenLen <= 15 and tokenLen >= 1:
                        lenClass = "short"
                    elif tokenLen <= 37 and tokenLen >= 16:
                        lenClass = "medium"
                    elif tokenLen <= 68 and tokenLen >= 38:
                        lenClass = "long"
                    else:
                        lenClass = None 
                        
                    pos = []
                    if loc == "middle" and lenClass == "medium":
                        POSWordBefore = pos_tags[citeLoc - 1][1]
                        POSWordAfter = pos_tags[citeLoc + 1][1]
                        
                        nouns = ["NN", "NNS", "NNP", "NNPS"]
                        verbs = ["VB", "VBD", "VBG", "VBP", "VBZ", "VBN"]
                        adj = ["JJ", "JJR", "JJS"]
                        adv = ["RB", "RBR", "RBS"]
                        pronoun = ["PRP", "PRP$", "WP", "EX"]
                        prepos = ["IN", "TO"]
                        others = ["PDT", "DT", "CC", "MD", "WDT", "POS", "RP", "FW", "CD", "WRB"]
                        
                        
                        if POSWordBefore in nouns:
                            pos.append("before_noun")
                        elif POSWordBefore in prepos:
                            pos.append("before_preposition")
                        elif POSWordBefore in verbs:
                            pos.append("before_verb")
                        elif POSWordBefore in adj:
                            pos.append("before_adjective")
                        elif POSWordBefore in adv:
                            pos.append("before_adverb")
                        elif POSWordBefore in pronoun:
                            pos.append("before_pronoun")
                        else:
                            pos.append("before_others")
                            
                        if POSWordAfter in nouns:
                            pos.append("after_noun")
                        elif POSWordAfter in prepos:
                            pos.append("after_preposition")
                        elif POSWordAfter in verbs:
                            pos.append("after_verb")
                        elif POSWordAfter in adj:
                            pos.append("after_adjective")
                        elif POSWordAfter in adv:
                            pos.append("after_adverb")
                        elif POSWordAfter in pronoun:
                            pos.append("after_pronoun")
                        else:
                            pos.append("after_others")
                    punc = None
                    puncWordList = [word for word in words]
                    
                    refCiteLoc = puncWordList.index("REF") 
                    twoAfter = puncWordList[refCiteLoc + 2]
                    
                    if twoAfter == ",":
                        punc = "comma"
                    elif twoAfter == ".":
                        punc = "period"
                    
                    
                    
                        
                                                        
                    obj = {
                                "tokenLen" : tokenLen,
                                "positionClass":loc,
                                "lengthClass" : lenClass,
                                "citedSent": parsedContext[0],
                                "citedText": parsedContext[1],
                                "cited": True,
                                "posClass":pos,
                                "worthClass":punc,
                                "lowClass": True
                    }
                    citing["citeInfo"] = obj
                    ob = { "$set": { "citeInfo": obj } }
                            # mc.update(db, "citedData", {"_id": citing["_id"]}, ob)
                    contextList.append(obj)
                
            
    else:
        
        cp = CitationParse()
                                    
        styles = [
                    cp.citationStyleRound
                ]

        parsedContext = None
        for style in styles:
            parsedContext = style(citing, None, None)

        if parsedContext is None:
            context = citing
            pattern = r"[A-Za-z]{3,},"
            match = re.findall(pattern, context)
            if len(match) == 1:
                match = re.search(pattern, context)
                end_index = match.end()
                
                context = context[:end_index - 1] + " <REF>" + context[end_index - 1:]
                punc = "comma"
            else:
                context = context[:len(context) - 1] + " <REF>" + context[len(context) - 1]
                
                punc = "period"
                    
            words = nltk.word_tokenize(context)
                        
            wordList = [word for word in words if word not in string.punctuation]    
                
            tokenLen = len(wordList)

            if tokenLen <= 15 and tokenLen >= 1:
                lenClass = "short"
            elif tokenLen <= 37 and tokenLen >= 16:
                lenClass = "medium"
            elif tokenLen <= 68 and tokenLen >= 38:
                lenClass = "long"
            else:
                lenClass = None 
                    
            obj = {
                                "tokenLen" : tokenLen,
                                "lengthClass" : lenClass,
                                "citedSent": context,
                                "cited": False,
                                "worthClass": punc,
                                "positionClass":""
            }
            
            contextList.append(obj)

            # for token in splitContext:
            #     if not token.is_punct:
            #         filteredText.append(token)
                    
            # print(filteredText)
                    
            # filtered_text.append(token.text)

            # # Get length of the context
            # wordsLen = len(new_con.split())
                    
            # if parsedContext:
            #     obj = {
            #         "parsedContext": parsedContext[0],
            #         "citedText": parsedContext[1],
            #         "tokenLen": len(parsedContext[0].split(" "))
            #     }
    
    return contextList

# if __name__ == "__main__":
#     db = mc.connect()

#     start_time = time.time()

#     # # cu = CiteUpdate()
    
#     # Define the batch size and number of worker processes
#     batch_size = 100
#     num_processes = 40

#     # Find the total number of documents in the collection
#     total_documents = mc.total_records(db,"citedData")
#     # print(total_documents)
#     # total_douments = 100
#     # Calculate the number of batches based on the batch size
    
#     num_batches = (total_documents // batch_size) + 1

#     # Create a multiprocessing pool
#     with Pool(processes=num_processes) as pool:
#         for batch_number in range(num_batches):
#             # Calculate the starting and ending indices for the current batch
#             start_index = batch_number * batch_size
#             end_index = start_index + batch_size
#             db = mc.connect()

#             # # Retrieve a batch of documents from the collection
#             records = mc.retrieve_records(db,"citedData",start_index,batch_size)
         
                
#             # Convert the documents to a list and process the batch in parallel
#             pool.map(filterData, (records,))
            
#     print(time.time() - start_time)
