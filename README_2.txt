First decompress the files.

To run the create index program issue the command:
python queryIndex.py stopWords.dat Inverted_Index.dat Title_Index.dat testCollection.dat


stopwords.dat is the file which contains the list of stopwords.
Collection.dat is our corpus.
Inverted_Index.dat is the output of the program which is the inverted index
Title_Index.dat is the output of the program which will contain the title of all the docs wiht corresponding docId.

Then enter the query as wela as the number 1,2,or 3 when prompt asks you to do so.
Enter phrase queries in qoutes("..")
:) 