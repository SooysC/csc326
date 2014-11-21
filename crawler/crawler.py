
# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import sqlite3 as lite
from pagerank import page_rank


def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""

        # Database Initialization
        self._db_conn = db_conn
        self._db_cursor = db_conn.cursor()
        self.create_databases()

        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        self._inverted_index_cache = { } 
        self._resolved_inverted_index_cache = { }
        self._links_cache = [ ]

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass

    def create_databases(self):
        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS Lexicon(word_id INTEGER PRIMARY KEY, word TEXT NOT NULL UNIQUE);')
        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS InvertedIndex(word_id INTEGER NOT NULL UNIQUE, doc_ids TEXT NOT NULL);')
        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS PageRank(doc_id INTEGER NOT NULL UNIQUE, doc_rank FLOAT);')
        self._db_cursor.execute('CREATE TABLE IF NOT EXISTS DocIndex(doc_id INTEGER PRIMARY KEY, doc_url TEXT UNIQUE);')

    def insert_document_to_db(self, url): # Erik
        """A function that inserts a url into a document db table
        and then returns that newly inserted document's id."""
        self._db_cursor.execute('INSERT INTO DocIndex(doc_url) VALUES("%s");' %  url)
        self._db_cursor.execute('SELECT doc_id FROM DocIndex WHERE doc_url = "%s"' % url)
        doc_id = self._db_cursor.fetchone()[0]
        assert(doc_id > 0)
        return doc_id
    
    def insert_word_to_db(self, word): # Erik
        """A function that inserts a word into the lexicon db table
        and then returns that newly inserted word's id."""
        self._db_cursor.execute('INSERT INTO Lexicon(word) VALUES("%s");' %  word)
        self._db_cursor.execute('SELECT word_id FROM Lexicon WHERE word = "%s"' % word)
        word_id = self._db_cursor.fetchone()[0]
        assert(word_id > 0)
        return word_id

    def insert_pagerank_to_db(self):
        """ Insert rankings of pages/documents to database"""
        rankings = page_rank(self._links_cache)
        for doc_id, doc_rank in rankings.iteritems():
            self._db_cursor.execute('INSERT INTO PageRank(doc_id, doc_rank) VALUES (%d, %f);' % (doc_id, doc_rank) )

    def insert_inververted_index_to_db(self):
        """ Insert rankings of pages/documents to database"""
        for word_id, doc_ids in self._inverted_index_cache.iteritems():
            self._db_cursor.execute('INSERT INTO InvertedIndex(word_id, doc_ids) VALUES (%d, "%s");' % (word_id, ','.join(str(x) for x in doc_ids)) )


    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        word_id = self.insert_word_to_db(word)
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        doc_id = self.insert_document_to_db(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        self._links_cache.append( (from_doc_id, to_doc_id) ) # Erik

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        self._url_queue.append((dest_url, self._curr_depth)) # add the just found URL to the url queue
        
        self.add_link(self._curr_doc_id, self.document_id(dest_url)) # add a link entry into the database from the current document to the other document

        # TODO add title/alt/text to index for destination url
    
        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document

        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            word_id = self.word_id(word)
            self._curr_words.append((word_id, self._font_size))

            if word_id in self._inverted_index_cache:
                self._inverted_index_cache[word_id].add(self._curr_doc_id)
                self._resolved_inverted_index_cache[word].add(self._curr_url)
            else:
                self._inverted_index_cache[word_id] = set([self._curr_doc_id])
                self._resolved_inverted_index_cache[word] = set([self._curr_url])
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come across some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()
            # skip this url; it's too deep
            if depth_ > depth: # depth  = input from the user
                continue # goes to next iteration of the loop

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue # skip / go to next iteration of the loop if already seen

            seen.add(doc_id) # add this document in "seen/visited" list
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

        self.insert_pagerank_to_db()
        self.insert_inververted_index_to_db()

        self._db_conn.commit()
        self._db_conn.close()

    def get_inverted_index(self):
        """Get the inverted index"""
        return self._inverted_index_cache

    def get_resolved_inverted_index(self):
        """Get the resolved inverted index"""
        return self._resolved_inverted_index_cache

    def get_links(self):
        """Get the links between pages for PageRank"""
        return self._links_cache

if __name__ == "__main__":
    db_conn = lite.connect("dbFile.db")
    bot = crawler(db_conn, "urls.txt")
    bot.crawl(depth=1)
