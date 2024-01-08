import sys
sys.path.append("/home/pop533611/thesis")
import mongoConnect as mc
import pandas as pd

def convert():
    # citedLoc = mc.read_records("citedLoc")
    # df = pd.DataFrame(citedLoc)
    # df = df.drop('_id', axis=1)
    # df.to_parquet("/dataHDD1/pmData/movingFile/citedLoc.parquet")
    # citingLoc = mc.read_records("citingLoc")
    # df = pd.DataFrame(citingLoc)
    # df = df.drop(['_id','citingPaper'], axis=1)
    # df.to_parquet("/dataHDD1/pmData/movingFile/citingLoc.parquet")
    citingTextLoc = mc.read_records("citingTextLoc")
    df = pd.DataFrame(citingTextLoc)
    df = df.drop(['_id','citingPaper'], axis=1)
    df.to_parquet("/dataHDD1/pmData/movingFile/citingTextLoc.parquet")
    
    
    

if __name__ == "__main__":
    convert()
