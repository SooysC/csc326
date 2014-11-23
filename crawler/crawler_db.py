import sqlite3 as lite

def connect_to_db(db_file = "../crawler/dbFile.db"):
    con = lite.connect(db_file)
    cur = con.cursor()
    return con, cur

def get_doc_ids_from_db(con, cur, word):
    cur.execute('SELECT InvertedIndex.doc_ids FROM Lexicon INNER JOIN InvertedIndex ON Lexicon.word_id = InvertedIndex.word_id WHERE Lexicon.word = "%s"' % word)

    try:
        doc_ids = cur.fetchone()[0]
    except:
        doc_ids = []
    return doc_ids

def get_doc_urls_from_db(con, cur, doc_ids):
    cur.execute('SELECT DocIndex.doc_url, PageRank.doc_rank FROM DocIndex LEFT JOIN PageRank ON DocIndex.doc_id = PageRank.doc_id WHERE DocIndex.doc_id IN (%s)' % doc_ids)
    doc_urls = cur.fetchall()
    sorted_doc_urls = sorted(doc_urls, key=lambda doc: doc[1], reverse=True)
    return [url[0] for url in sorted_doc_urls ]

def get_sorted_urls(word, db_file="../crawler/dbFile.db"):
    con, cur = connect_to_db(db_file)

    doc_ids = get_doc_ids_from_db(con, cur, word)
    if doc_ids == []:
        return []
    else:
        return get_doc_urls_from_db(con, cur, doc_ids)
