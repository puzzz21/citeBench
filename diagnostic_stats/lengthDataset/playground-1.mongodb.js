/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use('citation');

// Search for documents in the current collection.
db.getCollection('citingText')
  .find(
    {"citingCID":4253994}
  )
