# Word Counter
Implementation of Google Docs API for counting words on a Docs File.

To use, a `credentials.json` file needs to be added to the directory, that can be obtained on Google Cloud.

Finally, the document ID, easily obtained on the URL of the Docs file, needs to be given to the `document_id` variable on the `text-extractor-googledocs.py` (also in the `quickstart.py`)

PS: `text-extractor-googledocs.py` was desgined to benefit a specific need. To work properly with others documents, functions like `count_words_from_book()`, `average_words_per_chapter`, `print_word_counter()` and a bit of `main()` will have to be modified.
