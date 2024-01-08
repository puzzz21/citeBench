import json
import codecs
import polars as pl
from transformers import AutoTokenizer, OPTForCausalLM
import re
from tqdm import tqdm
import click 

# @click.command()
# @click.option("--datasetname", required=True, type=click.Choice(['length', 'position', 'intent',"worth", 'low']), 
#               help="Name of the dataset. Pick among length, position, and intent")

def process():
    evalData = prepareData()
    evaluate125M(evalData)
    # evaluate1B(evalData)
    # evaluate6B(evalData)
    # evaluate30B(evalData)

def prepareData():
    with open('postProcessedMul.json') as data_file:    
        data = json.load(data_file)
    
    evalData = []
    for d in data:
        d["context"] = d["context"].replace("<REF>","[START_REF]")
        actualList = []
        for cited in d["citedPaperMetaInfo"]:
            print(cited)
            
            actual = cited["title"].strip() + ", " + cited["firstAuthor"].strip()
            actualList.append(actual)
            
        d["actualCite"] = actualList
        evalData.append(d)
            
    return evalData

def evaluate1B(evalData):
    finalRes = []
    tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-1.3b")
    model = OPTForCausalLM.from_pretrained("facebook/galactica-1.3b", device_map="auto")
    
    with tqdm(total=len(evalData), desc="Processing") as pbar:
        for data in evalData:
            input_text = data["context"][0]["citedSent"]

            input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
            
            num_predictions = 10
            temperature = 0  # Adjust the temperature (higher for more randomness, lower for less)
            output_sequences = []

            for _ in range(num_predictions):
                # Generate one sequence with randomness
                output_sequence = model.generate(input_ids, max_length=175, do_sample=True, top_k=50,
                top_p=0.95,
                num_return_sequences=3)
                
                predicted = tokenizer.decode(output_sequence[0])
                t = predicted.split("[START_REF]")
                if len(t) > 1:
                    pred_text = t[1].split("[END_REF]")[0]
                    text = re.sub(r'^\W+', '', pred_text).strip()
   
                    output_sequences.append(text)
#             print(output_sequences)    
            data["predictedCite"]  = output_sequences   
            pbar.update(1)
            finalRes.append(data)

    file_path = "galPostion1B2.json"

    #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(finalRes, json_file, indent=4,ensure_ascii=False) 
        
        
def evaluate6B(evalData):
    tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-6.7b")
    model = OPTForCausalLM.from_pretrained("facebook/galactica-6.7b", device_map="auto")
    finalRes = []
    
    
    with tqdm(total=len(evalData), desc="Processing") as pbar:
            for data in evalData:
                input_text = data["context"][0]["citedSent"]

                input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
                
                num_predictions = 10
                temperature = 0  # Adjust the temperature (higher for more randomness, lower for less)
                output_sequences = []

                for _ in range(num_predictions):
                    # Generate one sequence with randomness
                    output_sequence = model.generate(input_ids, max_length=175, do_sample=True, top_k=50,
                    top_p=0.95,
                    num_return_sequences=3)
                    
                    predicted = tokenizer.decode(output_sequence[0])
                    t = predicted.split("[START_REF]")
                    if len(t) > 1:
                        pred_text = t[1].split("[END_REF]")[0]
                        text = re.sub(r'^\W+', '', pred_text).strip()
    
                        output_sequences.append(text)
    #             print(output_sequences)    
                data["predictedCite"]  = output_sequences   
                pbar.update(1)
                finalRes.append(data)
        
    file_path = "galInten6B1.json"

    #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(finalRes, json_file, indent=4,ensure_ascii=False) 
    
       
def evaluate125M(evalData):
    tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-125m")
    model = OPTForCausalLM.from_pretrained("facebook/galactica-125m", device_map="auto")
    finalRes = []
     
    
    with tqdm(total=len(evalData), desc="Processing") as pbar:
        for data in evalData:
            input_text = data["context"][0]["citedSent"]

            input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
            outputs = model.generate(input_ids, max_new_tokens=100)
            predicted = tokenizer.decode(outputs[0])
            t = predicted.split("[START_REF]")
            if len(t) > 1:
                pred_text = t[1].split("[END_REF]")[0]
                text = re.sub(r'^\W+', '', pred_text).strip()
                data["predictedCite"]  = text        
                pbar.update(1)
                finalRes.append(data)
        
    file_path = "galLength125m.json"

    #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(finalRes, json_file, indent=4,ensure_ascii=False) 


def evaluate30B(evalData):
    tokenizer = AutoTokenizer.from_pretrained("facebook/galactica-30B")
    model = OPTForCausalLM.from_pretrained("facebook/galactica-30B", device_map="auto")
    finalRes = []
    
    
    with tqdm(total=len(evalData), desc="Processing") as pbar:
        for data in evalData:
            input_text = data["context"][0]["citedSent"]

            input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
            outputs = model.generate(input_ids, max_new_tokens=100)
            predicted = tokenizer.decode(outputs[0])
            t = predicted.split("[START_REF]")
            if len(t) > 1:
                pred_text = t[1].split("[END_REF]")[0]
                text = re.sub(r'^\W+', '', pred_text).strip()
                data["predictedCite"]  = text        
                pbar.update(1)
                finalRes.append(data)
        
    file_path = "galLength30B.json"

    #     # # Open the file in write mode and write the data
    with open(file_path, "w") as json_file:
        json.dump(finalRes, json_file, indent=4,ensure_ascii=False) 


if __name__ == '__main__':
    process()


