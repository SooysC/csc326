from bottle import route, run
from bottle import static_file
from bottle import get, post, request, template, debug
import operator
# Global in-memory store of the keywords that come in
dictionary = dict()
current_dictionary = dict()
@route('/', method = 'GET')	
def returnHomePage():
	filename = "index.html"	
	return static_file(filename, root='../html/')

@route('/', method = 'POST')
def processQuery():
	keywords =  request.forms.get('keywords')
	if keywords:
		print 'keywords:', keywords
		# tokenize keywords 
		currentKeywordList = keywords.split(' ')
		current_dictionary = {}
		print 'Current keywords:', currentKeywordList
		
		# and throw them into dictionary
		for word in currentKeywordList:
			if word in dictionary:
				currentCount = dictionary.get(word)
				dictionary[word] = currentCount + 1
				current_dictionary[word] = dictionary[word]
			else:
				dictionary[word] = 1
				current_dictionary[word] = dictionary[word]
		
		sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1))
		popular = list(reversed(sorted_dictionary))		
		popular = popular[:20]
		print 'Dictionary is:', dictionary
		print 'sorted_dictionary is:', sorted_dictionary
		print 'current_dictionary is:', current_dictionary
		print '20 items:', popular
		# Need to display the current set of input keywords, and the count of those keywords
		output = template('make_table', wordList=current_dictionary, popularWords=popular)
		return output
	else:
		filename = "index.html"	
		return static_file(filename, root='../html/')
run(host = 'localhost', port = 8080, debug = True)

