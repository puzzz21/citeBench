from pymongo import MongoClient
from multiprocessing import Pool, Manager

# Define the function to process a batch of documents
def process_batch(batch):
    client = MongoClient('mongodb://localhost:23567',maxPoolSize=1000)


    # Perform your desired operations on the batch of documents
    for document in batch:
        print(document)
        # Process each document as needed
        
    client.close()


def main():
    num_processes = 4
    batch_size = 1

    # Create a multiprocessing manager

    #  the shared MongoClient instance inside the manager
    

    # Create a multiprocessing pool
    with Pool(processes=num_processes) as pool:
        with open('dump.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

            for i in range(0, len(lines), batch_size):
                data = lines[i:i+batch_size]
                pool.apply_async(process_batch, (data))

        # Close the pool and wait for all tasks to complete
        pool.close()
        pool.join()

    # Close the MongoClient connection after all tasks are completed

if __name__ == '__main__':
    main()