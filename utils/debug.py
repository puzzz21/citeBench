import mongoConnect as mc
import json

with open('../s2orc/data1.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()[:100]
    
    
for i,line in enumerate(lines):
    l = json.loads(line)
    text = l["content"]["text"]
    title = l["content"]["annotations"]["title"]
    bibEntry = l["content"]["annotations"]["bibentry"]
    bibRef = l["content"]["annotations"]["bibref"]
    if title is not None:
        title = json.loads(title)[0]
        titleText = text[int(title["start"]):int(title["end"])].encode('utf-8').decode('unicode_escape')
        # print(titleText.lower())
        if titleText.lower() == "How digitalization reinvented entrepreneurial resilience during COVID-19".lower():
            for b in json.loads(bibRef):
                for bb in json.loads(bibEntry):
                    if "attributes" in bb and "attributes" in b:
                        if bb["attributes"]["id"] == b["attributes"]["ref_id"]:
                            x = text[int(b["start"]):int(b["end"])]
                            print(x)
                        
                        
                
                    # print(b["attributes"]["ref_id"])
                    
                    
                    # print(x)

            # with open('debug.json', 'w', encoding='utf-8') as file:
            #     file.write(json.dumps(l))
    # if l["content"]["source"]["pdfsha"] == "60680a7b5ff0d7497dd9060624f31b16debb9c4a":
    #     print(l)
    
    

# 60680a7b5ff0d7497dd9060624f31b16debb9c4a


