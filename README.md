csc326
======

### To Run:
1. run `python csc326/bottle-0.12.7/feServer.py`
1. go to `http://54.173.22.59/`

### To Test `crawler.py`
1. run `python csc326/crawler/crawler_tester.py`

### To run the AWS initialization scirpt:
1. go to csc326/aws/
2. run 'python csc326/aws/lab2_aws_setup.py'

### To view the benchmark reports,
1. go to csc326/aws/
2. run 'vim reports.txt'
### brought to you by team 25 of CSC326:
1. Samprit Raihan (raihansa)
1. Jon Erik Suero (suerojon)


Tables:
Word
- word
- word_id
- documents ?

self._inverted_index_cache()

word_id: (doc_id, doc_id,...)

Document
- url # string
- document_id # int
- rank # float

##### to find
1.) Input: word
2.) Get: word: {document_id, document_id, ...}
3.) Get: {document, document}
4.) Sort by rank: {document, document}
5.) Output: {document, document}

######

store Document{url, doc_id}
store Document.where(doc_id){rank}
store 

######
Lexicon:
>> Word
<< Word_id

	Lexicon
		- word # string unique
		- word_id # integer

Inverted Index:
>> Word_id
<< Doc_ids

	InvertedIndex
		- word_id # integer
		- doc_ids # string (csv)

PageRank:
>> Doc_ids
<< (Doc_id, Rank), (Doc_id, Rank), ...

	PageRank:
		- doc_id # integer
		- rank # float

~~ Sort:
(Doc_id, Rank), (Doc_id, Rank), ...


Doc Index:
>> Doc_ids # sorted
<< Doc_urls

	DocIndex:
		- doc_id # integer
		- doc_url # string
		- other stuff maybe...
  