                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  /* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use('citation');

const collection = db.collection(collectionName);

  // Use the distinct method to retrieve unique values
  const uniqueValues = await collection.distinct(fieldName);




// Sort the documents in descending order based on the _id field and limit to the last 1298 documents.
var documentsToDelete = db.apiData.find({"chunk":15}).sort({ "_id": -1 }).limit(1298);

// Delete the selected documents.
documentsToDelete.forEach(function(doc) {
    db.apiData.deleteOne({ "_id": doc._id });
});

// Search for documents in the current collection.
db.getCollection('meta')
  .find(
    {
        pId: "be40bf4a92712ca52d0859e8acae45e118b49db7"
      /*
      * Filter
      * fieldA: value or expression
      */
    },
    {
      /*
      * Projection
      * _id: 0, // exclude _id
      * fieldA: 1 // include field
      */
    }
  )
  .sort({
    /*
    * fieldA: 1 // ascending
    * fieldB: -1 // descending
    */
  });
