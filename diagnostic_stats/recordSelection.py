import pandas as pd
import polars as pl
import pandas as pd
import sys
sys.path.append("/abyss/home/citation-recommendation/utils")
import mongoConnect as mc
from API_request import APIRequest
from finalIds import ids
import random
import uuid

import click
import time


api = APIRequest()

fileName = {
    "length": "Length",
    "position": "Position",
    "intent": "Intent",
    "worth": "WorthNew",
    "pos": "Pos",
    "low":"Low"
}

@click.command()
@click.option("--dataset", required=True, type=click.Choice(['length', 'position', 'intent','worth','pos', "low"]),
              help="Name of the dataset. Pick among length, position, intent, worth, and pos")
@click.option("--samplesperclass", required=True, help="Number of samples per classs")

def process(dataset,samplesperclass):
    rc = RecordSelection(dataset,samplesperclass)
    print(dataset,samplesperclass)
    fr = rc.filterRecords()
    fg = rc.filterGroups(fr[0],fr[1])
    samples = rc.extractSamples(fg)
    combined = rc.combineSampleAndPaperInfo(samples)
    citedPapers = rc.parseCitedPapers(combined)
    citingPapers = rc.parseCitingPapers(citedPapers)
    rc.retrieveCitingText(citingPapers)

class RecordSelection:

    def __init__(self, dataset, samplesPerClass):
        self.dataset = dataset
        self.recordsPerSampleClass = int(samplesPerClass)
        self.inputParquet = "/local/combinedPapers.parquet"
        self.yearGroup = [(1996, 2000), (2001, 2005), (2006, 2010), (2011, 2015), (2016, 2020)]
        # self.yearGroup = [(1996, 2000)]

        self.fieldThreshold = 3
        self.ids = ids
        self.lowCategory = ["Psychology","Environmental Science","Engineering","Business","Geography","Political Science","Sociology","Geology","History","Art", "Philosophy"]
        self.highCategory = ["Medicine","Physics","Biology","Computer Science","Mathematics","Chemistry","Materials Science"]
        # self.highCategory = ["Medicine"]

        if dataset == "low":
            self.cats = self.lowCategory
        else:
            self.cats = self.highCategory
            
        if dataset == "low":
            self.fieldThreshold = 0

            
        
    def filterRecords(self):
        # Read data from the Parquet file
        papers = pl.read_parquet(self.inputParquet)
        print(papers.columns)

        # Explode the 's2fieldsofstudy' column
        df_exploded = papers.explode('s2fieldsofstudy')

        # Extract exploded list
        exploded_list = [i for i in df_exploded["s2fieldsofstudy"]]

        # Create a DataFrame from the exploded list
        df_sep = pl.from_dicts(exploded_list)

        # Combine exploded DataFrame with the original DataFrame
        df_res = df_exploded.with_columns(df_sep)

        # Filter records
        df_filter = df_res.filter((pl.col("source") == "external") & (pl.col("isopenaccess") == True))

        # Cast 'year' column to Int32
        df_filter = df_filter.with_columns(
            pl.col("year").cast(pl.Int32).alias("year")
        )

        # Group by 'category' column
        grouped = df_filter.groupby('category')

        return (df_filter,grouped)

    def filterGroups(self,df_filter,grouped):
        # Initialize empty DataFrames and lists to store results
        df = pd.DataFrame()
        filter_list = []  # List to store filtered DataFrames
        catList = []  # List to store category values
        yearList = []  # List to store year values
        ccListDF = []  # List to store citationcount values
        yearsCount = 0  # Counter for total years
        cCount = 0  # Counter for total records
        c = 0  # Counter for total categories

        # Select columns and add a 'group' column filled with None
        df_filter = df_filter.select(["corpusid", "year", "citationcount", "category"])
        df_filter = df_filter.with_columns(pl.lit(None).alias("group"))

        # Iterate through categories and their groups
        for cat, group in grouped:
            
            if cat in self.cats:
                print(cat)
                
                c += len(group)  # Increment category counter

                # Calculate the percentage of records in the current group
                per = (len(group) / len(df_filter)) * 100

                if per >= self.fieldThreshold:
                    for i in self.yearGroup:
                        # Filter the group based on the year range
                        group_filter = group.filter(pl.col("year").is_in(list(range(i[0], i[1] + 1))))
                        print("----------------------")
                        yearsCount += len(group_filter)  # Increment total years counter

                        ccList = group_filter["citationcount"].to_list()
                        cc = sorted(set(ccList))

                        if len(cc) > 10:
                            elements_per_group = int(len(cc) / 10)
                            groups = [cc[i:i + elements_per_group] for i in range(0, len(cc), elements_per_group)]
                            for ind, j in enumerate(groups[:10]):
                                catList.append(cat)
                                yearList.append(str(i))
                                ccListDF.append(str(j))

                                # Filter the DataFrame and add the 'group' column
                                df_filter_1 = df_filter.filter(
                                    (df_filter["category"] == cat) &
                                    df_filter["year"].is_in(list(range(i[0], i[1] + 1))) &
                                    df_filter["citationcount"].is_in(j)
                                ).with_columns(
                                    pl.lit(ind).alias("group")
                                )
                                cCount += len(df_filter_1)  # Increment total records counter
                                filter_list.append(df_filter_1)

        # Create a DataFrame from the lists
        df["field"] = catList
        df["year"] = yearList
        df["cc"] = ccListDF

        # Concatenate the filtered DataFrames
        concatenated_df = pl.concat(filter_list)
        return concatenated_df

    def extractSamples(self,df):
        # Group the DataFrame by 'category'
        grouped = df.groupby('category')

        final = []  # Initialize a list for the final result
        data = []  # Initialize a list for data

        c = 0  # Initialize a counter

        # Iterate through categories and their groups
        for cat, grp in grouped:

            # Iterate through year ranges and group indices
            for i in self.yearGroup:
                for j in range(10):

                    # Filter the group based on year, group index, and citation count
                    grp_test = grp.filter(
                        (pl.col("year").is_in(list(range(i[0], i[1] + 1)))) &
                        (pl.col("group") == j) &
                        (pl.col("citationcount") >= 5) &
                        (~pl.col("corpusid").is_in(self.ids))
                    )

                    # Get a list of 'corpusid' values from the filtered group
                    grp_test_list = grp_test["corpusid"].to_list()

                    # print(str(i[0]) + "-" + str(i[1] + 1) + ":" + str(j) + ":" + str(len(grp_test_list)))

                    # Shuffle the 'corpusid' list randomly
                    random.shuffle(grp_test_list)

                    # Filter the DataFrame and add to  data
                    filtered_df = grp_test.filter(pl.col("corpusid").is_in(grp_test_list[:self.recordsPerSampleClass]))[:self.recordsPerSampleClass]
                    # print(len(self.ids))
                    self.ids = self.ids + list(filtered_df["corpusid"])
                    # print(len(self.ids))
                    data.append(filtered_df)

            print("=================================================")
        
        result = pl.concat(data)
        # print("lendata: ",result)
        # Concatenate the data
        return result

    def combineSampleAndPaperInfo(self, data):
        dataList = []  # Initialize a list to store joined DataFrames
        res = []  # Initialize a list to store filtered DataFrames

        # Iterate over a range of indices
        for i in range(30):
            # Read data from a Parquet file based on the index 'i'
            text = pl.read_parquet(f"/local/s2orc/{i}.parquet")
            filtered_df = text.filter( ~pl.col('content.annotations.abstract').is_null())

            # print("columns:: ", text.columns)
            print("text:::: ", filtered_df.columns)

            # Join the 'data' DataFrame with the 'text' DataFrame on the 'corpusid' column
            joined = data.join(filtered_df, on="corpusid")
            dataList.append(joined)  # Append the joined DataFrame to 'dataList'

        # Iterate over the joined DataFrames in 'dataList'
        for x in dataList:
            # Drop unnecessary columns from the joined DataFrame
            x = x.drop(['content.source.oainfo', 'content.source.oainfo.license', 'content.source.oainfo.openaccessurl',
                        'content.source.oainfo.status'])
            res.append(x)  # Append the filtered DataFrame to 'res'


        # Concatenate the filtered DataFrames
        return pl.concat(res)

    def parseCitedPapers(self, df):
        # Drop the "content.source.pdfurls" column from the DataFrame
        df = df.drop("content.source.pdfurls")
        print("df cols:: ", df.columns)
        df = df.to_pandas()

        # Convert the DataFrame to a list of dictionaries
        data_records = df.to_dict(orient='records')

        # Save the list of dictionaries to the "cited" collection in the MongoDB database
        mc.insert_many("cited" + fileName[self.dataset], data_records)

        return data_records

    def parseCitingPapers(self,records):
        # records = mc.read_records("citedTypePatches")
        # df = pl.DataFrame(records)
        # df = df.to_pandas()

        # # Convert the DataFrame to a list of dictionaries
        # records = df.to_dict(orient='records')
        
        dataList = []  # Initialize a list to store data records
        for document in records:

            if "content.source.pdfsha" in document and document["content.source.pdfsha"]:
                # Retrieve citing data using the 'pdfsha' value
                doc = api.getCitingData(document["content.source.pdfsha"])
                if "data" in doc:
                    data = doc["data"]
                    for d in data:
                        # Check if the citing paper meets certain criteria
                        if d["citingPaper"]["isOpenAccess"] and d["citingPaper"]["abstract"] and d["citingPaper"]["year"] and d["citingPaper"]["title"] \
                                and d["citingPaper"]["publicationDate"] and d["citingPaper"]["journal"] and \
                                d["citingPaper"]["authors"]:
                            obj = {
                                "citingCID": d["citingPaper"]["corpusId"],
                                "citingId": d["citingPaper"]["paperId"],
                                "meta": d,
                                "citedPaperId": document["content.source.pdfsha"],
                                "citedPaperCId": document["corpusid"],
                                "citingPaper": document["_id"]
                            }
                            dataList.append(obj)  # Append the object to the data list

                            # Save the object to the "citingLoc" collection in the MongoDB database
                            mc.insert_record("citing" + fileName[self.dataset], obj)
        return pl.DataFrame(dataList)

    def retrieveCitingText(self,df):
        
        citingJoined = []  # Initialize a list to store joined DataFrames
        for i in range(30):
            print("=================================")
            print(i)
            # Read data from a Parquet file based on the index 'i'
            text = pl.read_parquet("/local/s2orc/" + str(i) + ".parquet")

            # Join the 'df' DataFrame with the 'text' DataFrame using 'corpusid' columns
            citingJoined.append(df.join(text, right_on="corpusid", left_on="citingCID"))

        citingList = []  # Initialize a list to store filtered DataFrames
        for x in citingJoined:
            # Drop unnecessary columns from the joined DataFrame
            x = x.drop(['content.source.oainfo', 'meta', 'content.source.pdfurls', 'content.source.oainfo.license',
                        'content.source.oainfo.openaccessurl', 'content.source.oainfo.status'])
            citingList.append(x)

        # Concatenate the filtered DataFrames
        citingConcat = pl.concat(citingList)
        citingConcatPd = citingConcat.to_pandas()

        # Add a new '_id' column with unique values
        citingConcatPd['_id'] = [str(uuid.uuid4())[:24] for _ in range(len(citingConcatPd))]
        citingConcatRc = citingConcatPd.to_dict(orient="records")

        # Save the list of dictionaries to the "citingTextLoc" collection in the MongoDB database
        mc.insert_many("citingText" + fileName[self.dataset], citingConcatRc)

        # f = open("sampleIds.py", "w")
        # f.write("ids = " + str(ids))
        # f.close()

if __name__ == "__main__":
    start_time = time.time()
    process()
    print("--- %s seconds ---" % (time.time() - start_time))