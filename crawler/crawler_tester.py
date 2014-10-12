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

def test_inverted_index_with_two_urls():
    print "Test Inverted Index with Two URLs"
    c = crawler(None, 'urls2.txt')
    c.crawl()
    expected_inverted_index = {1: set([1]), 2: set([1]), 3: set([1]), 4: set([1]), 5: set([1]), 6: set([1]), 7: set([1]), 8: set([1]), 9: set([1]), 10: set([1]), 11: set([1]), 12: set([1]), 13: set([1]), 14: set([1]), 15: set([1]), 16: set([1]), 17: set([1]), 18: set([1]), 19: set([1]), 20: set([1]), 21: set([1]), 22: set([1]), 23: set([1]), 24: set([1]), 25: set([1]), 26: set([1]), 27: set([1]), 28: set([1]), 29: set([1]), 30: set([1]), 31: set([1]), 32: set([1]), 33: set([1]), 34: set([1]), 35: set([1]), 36: set([1]), 37: set([1]), 38: set([1]), 39: set([1]), 40: set([1]), 41: set([1]), 42: set([1]), 43: set([1]), 44: set([1]), 45: set([1]), 46: set([1]), 47: set([1]), 48: set([1]), 49: set([1]), 50: set([1]), 51: set([1]), 52: set([1]), 53: set([1]), 54: set([1]), 55: set([1]), 56: set([1]), 57: set([1]), 58: set([1]), 59: set([1]), 60: set([1]), 61: set([1]), 62: set([1]), 63: set([1]), 64: set([1]), 65: set([1]), 66: set([1]), 67: set([1]), 68: set([1]), 69: set([1]), 70: set([1]), 71: set([1]), 72: set([1]), 73: set([1]), 74: set([1]), 75: set([1]), 76: set([1]), 77: set([1]), 78: set([1]), 79: set([1]), 80: set([1]), 81: set([1]), 82: set([1]), 83: set([1]), 84: set([1]), 85: set([2]), 86: set([2]), 87: set([2])}
    if c.get_inverted_index() == expected_inverted_index:
        print "Success!"
    else:
        print "Fail! Wrong inverted_index"

   

test_inverted_index()
print ""
test_resolved_inverted_index()
print ""
test_empty_inverted_index()
print ""
test_empty_resolved_inverted_index()
print ""
test_inverted_index_with_two_urls()
