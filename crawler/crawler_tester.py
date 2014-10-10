from crawler import crawler

def test_inverted_index():
    print "Test Inverted Index"
    c = crawler(None, 'urls.txt')
    c.crawl()
    expected_inverted_index = {1: set([1]), 2: set([1]), 3: set([1])} 
    if c.get_inverted_index() == expected_inverted_index:
        print "Success!"
    else:
        print "Fail! Wrong inverted_index"

def test_resolved_inverted_index():
    print "Test Resolved Inverted Index"
    c = crawler(None, 'urls.txt')
    c.crawl()
    expected_resolved_inverted_index = {u'languages': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'csc326': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']), u'programming': set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html'])} 
    if c.get_resolved_inverted_index() == expected_resolved_inverted_index:
        print "Success!"
    else:
        print "Fail! Wrong resolved_inverted_index"

def test_empty_inverted_index():
    print "Test Empty Inverted Index"
    c = crawler(None, 'invalid.txt')
    c.crawl()
    expected_inverted_index = {} 
    if c.get_inverted_index() == expected_inverted_index:
        print "Success!"
    else:
        print "Fail! With invalid *.txt file, crawler must have empty inverted_index"

def test_empty_resolved_inverted_index():
    print "Test Empty Resolved Inverted Index"
    c = crawler(None, 'invalid.txt')
    c.crawl()
    expected_resolved_inverted_index = {} 
    if c.get_resolved_inverted_index() == expected_resolved_inverted_index:
        print "Success!"
    else:
        print "Fail! With invalid *.txt file, crawler must have empty resolved_inverted_index"


test_inverted_index()
test_resolved_inverted_index()
test_empty_inverted_index()
test_empty_resolved_inverted_index()
