import json   
import pandas as pd
import click

datasets = {
    "length" : ["short", "medium", "long"],
    "location" : ["start", "middle", "end"],
    "intent" : ["background", "methodology", "result"],
    "worth" : ["comma","period"],
    "pos" : ["before_verb","before_noun","before_adjective","before_adverb","before_pronoun","before_preposition","before_others",
             "after_verb","after_noun","after_adjective","after_adverb","after_pronoun","after_preposition","after_others"],
    "low":["Psychology","Environmental Science","Engineering","Business","Geography","Political Science","Sociology","Geology","History","Art", "Philosophy"]
}

models = {
    "lcr": "Local-Citation-Recommendation",
    "ncn": "neural_citation"
}

@click.command()
@click.option("--dataset", required=True, type=click.Choice(['length', 'location', 'intent',"low", "pos"]), 
              help="Name of the dataset. Pick among length, position, and intent")
@click.option("--method", required=True, type=click.Choice(['mrr','recall']), 
              help="Name of method.")
@click.option("--model", required=True, type=click.Choice(['ncn','lcr']), 
              help="Name of model.")

def process(method,dataset,model):
    with open(f'{dataset}.json', 'r') as file:
        data = json.load(file)

    result = []
    if dataset == "low":
        for d in data:
            result.append(d["field"])
            
    else:
        for d in data:
            result.append(d["context"][0][f"{dataset}Class"])
            
            
        
    dataList = []
        
    for i in [1, 5,10,20,50,100]:
        obj = {}
        res = pd.read_pickle(f"/abyss/home/{models[model]}/output/{method}{dataset}_{i}")
        
        for datasetClass in datasets[dataset]:
            tempClass = []
            for j in range(len(res)):
                
                if dataset == "pos":
                    if datasetClass in result[j]:
                        tempClass.append(res[j])
                else:
                    if datasetClass == result[j]:
                        tempClass.append(res[j])
            
            if len(tempClass) == 0:
                obj[datasetClass] = 0
            else:
                obj[datasetClass] =  sum(tempClass) / len(tempClass)
        
        dataList.append({i : obj})    
            
        print(dataList)
        
        # mrrShort = sum(short) / len(short)
        # mrrMedium = sum(medium) / len(medium)
        # mrrLong = sum(longSent) / len(longSent)
        
        # ncnMRRResult.append({i : { "short" : mrrShort, "medium": mrrMedium, "long": mrrLong}})

    
# def ncnFilterMRR():
#     ncnMRRResult = []
#     for i in [1,5,10,20,50,100]:
#         res = pd.read_pickle(f"/abyss/home/neural_citation/output/mrrlength_{i}")
#         short = []
#         medium = []
#         longSent = []
#         for j in range(len(res)):
#             if result[j] == "short":
#                 short.append(res[j])
#             elif result[j] == "medium":
#                 medium.append(res[j])
#             else:
#                 longSent.append(res[j])

#         mrrShort = sum(short) / len(short)
#         mrrMedium = sum(medium) / len(medium)
#         mrrLong = sum(longSent) / len(longSent)
        
#         ncnMRRResult.append({i : { "short" : mrrShort, "medium": mrrMedium, "long": mrrLong}})
#     print("mrr: ", ncnMRRResult)

# def ncnFilterRecall():
#     ncnRecallResult = []
#     for i in [1,5,10,20,50,100]:
#         res = pd.read_pickle(f"/abyss/home/neural_citation/output/recalllength_{i}")
#         short = []
#         medium = []
#         longSent = []
#         for j in range(len(res)):
#             if result[j] == "short":
#                 short.append(res[j])
#             elif result[j] == "medium":
#                 medium.append(res[j])
#             else:
#                 longSent.append(res[j])
        
#         recallShort = sum(short) / len(short)
#         recallMedium = sum(medium) / len(medium)
#         recallLong = sum(longSent) / len(longSent)
        
#         ncnRecallResult.append({i : { "short" : recallShort, "medium": recallMedium, "long": recallLong}})
#     print("recall: ",ncnRecallResult)
                  
# def lcrFilterMRR():
    
#     lcrMRRResult = []
#     for i in [5,10,20,50,100]:
#         res = pd.read_pickle(f"/abyss/home/Local-Citation-Recommendation/output/mrrlength_{i}")
#         short = []
#         medium = []
#         longSent = []
#         for j in range(len(res)):
            
#             if result[j] == "short":
#                 short.append(res[j])
#             elif result[j] == "medium":
#                 medium.append(res[j])
#             else:
#                 longSent.append(res[j])

#         mrrShort = sum(short) / len(short)
#         mrrMedium = sum(medium) / len(medium)
#         mrrLong = sum(longSent) / len(longSent)
        
#         lcrMRRResult.append({i : { "short" : mrrShort, "medium": mrrMedium, "long": mrrLong}})
#     print("mrr: ", lcrMRRResult)

# def lcrFilterRecall():
#     lcrRecallResult = []
#     for i in [1,5,10,20,50,100]:
#         res = pd.read_pickle(f"/abyss/home/Local-Citation-Recommendation/output/recalllength_{i}")
#         short = []
#         medium = []
#         longSent = []
#         for j in range(len(res)):
#             if result[j] == "short":
#                 short.append(res[j])
#             elif result[j] == "medium":
#                 medium.append(res[j])
#             else:
#                 longSent.append(res[j])
        
#         recallShort = sum(short) / len(short)
#         recallMedium = sum(medium) / len(medium)
#         recallLong = sum(longSent) / len(longSent)
        
#         lcrRecallResult.append({i : { "short" : recallShort, "medium": recallMedium, "long": recallLong}})
#     print("recall: ",lcrRecallResult)
                  


# ncnFilterMRR()
# ncnFilterRecall()
# lcrFilterMRR()
# lcrFilterRecall()


if __name__ == "__main__":
    process()