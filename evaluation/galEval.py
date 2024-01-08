import json
import codecs
import polars as pl
from transformers import AutoTokenizer, OPTForCausalLM
import re
from tqdm import tqdm
import click 
import torch
torch.cuda.set_device(0)

from pymongo import MongoClient
import sys
from bson import ObjectId

sys.path.append("/abyss/home/citation-recommendation/utils")
import mongoConnect as mc

galParams = ["125m"]

@click.command()
@click.option("--dataset", required=True, type=click.Choice(['length', 'location', 'intent',"worth", 'low', 'pos']), 
              help="Name of the dataset. Pick among length, position, and intent")
@click.option("--k", required=True, type=click.Choice(['100']), 
              help="Name of the dataset. Pick among length, position, and intent")

def process(dataset, k):
    evalData = prepareData(dataset)
    for param in galParams:
        evaluate(evalData,param, int(k),dataset)

def prepareData(dataset):
    with open(f'galactica/{dataset}.json') as data_file:    
        data = json.load(data_file)
    
    evalData = []
    print("len data1 ",len(data))
    for d in data:
        d["context"][0]["citedSent"] = d["context"][0]["citedSent"].replace("<REF>","[START_REF]")
        actual = d["citedPaperMetaInfo"]["title"].strip() + ", " + d["citedPaperMetaInfo"]["firstAuthor"].strip()
        d["actualCite"] = actual
        evalData.append(d)
        
    return evalData[1153:]

def evaluate(evalData,param, k, dataset):
    print("len evalData2 ",len(evalData))
    finalRes = []
    tokenizer = AutoTokenizer.from_pretrained(f"facebook/galactica-{param}")
    model = OPTForCausalLM.from_pretrained(f"facebook/galactica-{param}", device_map="cuda")
    
    with tqdm(total=len(evalData), desc="Processing") as pbar:
        for data in evalData:
            
            input_text = data["context"][0]["citedSent"]

            input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
            
            num_predictions = k
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
            data["_id"] = ObjectId()
            mc.insert_record(f"gal125m{dataset}",data)
            finalRes.append(data)

    file_path = f"galactica/results/{dataset}.json"

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
            outputs = model.generate(input_ids, max_new_tokens=150)
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


