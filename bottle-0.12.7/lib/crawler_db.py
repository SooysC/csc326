import sqlite3 as lite
import words_analyzer


def connect_to_db(db_file = "../crawler/dbFile.db"):
    con = lite.connect(db_file)
    cur = con.cursor()
    return con, cur


def get_all_words(con, cur, char):

    cur.execute("SELECT word FROM Lexicon WHERE word LIKE '%c%%\'" % char)
    #cur.execute("SELECT word FROM Lexicon")
    return [w[0] for w in cur.fetchall()]


def get_doc_ids_from_db(con, cur, word):
    cur.execute('SELECT InvertedIndex.doc_ids FROM Lexicon INNER JOIN InvertedIndex ON Lexicon.word_id = InvertedIndex.word_id WHERE Lexicon.word = "%s"' % word)

    try:
        doc_ids = cur.fetchone()[0].split(",")
    except:
        doc_ids = []
    return doc_ids

# Deprecated, but keep it for now
def get_doc_urls_from_db(con, cur, doc_ids):
    cur.execute('SELECT DocIndex.doc_url, PageRank.doc_rank FROM DocIndex LEFT JOIN PageRank ON DocIndex.doc_id = PageRank.doc_id WHERE DocIndex.doc_id IN (%s)' % doc_ids)
    doc_urls = cur.fetchall()
    sorted_doc_urls = sorted(doc_urls, key=lambda doc: doc[1], reverse=True)
    return [url[0] for url in sorted_doc_urls ]


def get_all_sorted_urls(words, db_file="../crawler/dbFile.db"):
    con, cur = connect_to_db(db_file) # change to decorator later - Erik

    words_generator = words_analyzer.split(words)
    doc_ids = []
    recommended_words = []

    for word in words_generator:
        new_doc_ids = get_doc_ids_from_db(con, cur, word)
        if new_doc_ids == []:
            all_available_words = get_all_words(con,cur, word[0])
            recommended_words.append( words_analyzer.recommend(word, all_available_words) )
        else:
            recommended_words.append( word )
            doc_ids = list(set(doc_ids + new_doc_ids)) # remove duplicates

    recommended_words = ' '.join(recommended_words)
    recommended_words = "" if recommended_words==words else recommended_words

    con.close()
    return (doc_ids==[] and (recommended_words, [])) or (recommended_words, get_doc_urls_and_title_from_db(con, cur, ','.join(doc_ids)))


def get_doc_urls_and_title_from_db(con, cur, doc_ids, db_file="../crawler/dbFile.db"):
    con, cur = connect_to_db(db_file)
    cur.execute('SELECT DocIndex.doc_url, PageRank.doc_rank, DocIndex.doc_url_title FROM DocIndex LEFT JOIN PageRank ON DocIndex.doc_id = PageRank.doc_id WHERE DocIndex.doc_id IN (%s)' % doc_ids)
    doc_urls = cur.fetchall()
    sorted_doc_urls = sorted(doc_urls, key=lambda doc: doc[1], reverse=True)
    return [(url[0], url[2]) for url in sorted_doc_urls ]


def insert_pin_urls_to_db(email, url, db_file="../crawler/dbFile.db"):
    con, cur = connect_to_db(db_file)

    # Getting the url titles from DocIndex
    query = 'SELECT doc_url_title FROM DocIndex WHERE doc_url IN ("%s")' % url
    cur.execute(query)
    doc_url_title = cur.fetchone()[0]

    # Inserting email, url and url titles into PinTable, while ignoring duplicate entries
    query = 'INSERT OR IGNORE INTO PinBoard (email, doc_url, doc_url_title) VALUES ("%s", "%s", "%s")' % (email, url, doc_url_title)
    cur.execute(query)

    # Testing to see if it actually adds a lot of items to the table
    cur.execute('SELECT * FROM PinBoard')
    results = cur.fetchall()
    con.commit()
    con.close()

def get_pin_urls_from_db(email, db_file="../crawler/dbFile.db"):
    con, cur = connect_to_db(db_file)
    query = 'SELECT PinBoard.doc_url, PinBoard.doc_url_title FROM PinBoard WHERE email IN ("%s")' % email
    cur.execute(query)
    results = cur.fetchall()
    con.commit()
    con.close()
    return [(col[0], col[1]) for col in results]