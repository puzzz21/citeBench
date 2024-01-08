import sys
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc

def allIds():
    cols = ["finalIntents", "finalLocations","finalLow","finalPosWords","finalWorthsss","finalLengths"]
    allIds = []
    for col in cols:
        recs = mc.read_records(col)
        for rec in recs:
            if "citedPaper" in rec:
                print(rec["citedPaper"])
                allIds.append(rec["citedPaper"])
    
    with open("finalIds.py", "w") as file:
        file.write("ids = "+ str(allIds))

if __name__ == "__main__":   
   allIds()   