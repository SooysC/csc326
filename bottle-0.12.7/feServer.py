from bottle import route, run
from bottle import static_file
from bottle import get, post, request, template, debug
import operator

# Global in-memory store of the keywords that come in
dictionary = dict()
current_dictionary = dict()
current_dictionary = {}
popular = list()

@route('/', method = 'GET')
def processQuery():
	global dictionary
	global current_dictionary
	global popular
	print 'processQuery'
	
	keywords =  request.query_string
	
	print 'keywords--->', keywords
	if keywords == "":
		# return the home page
		print 'Gonna return the home page'
		output = template('./empty_string_table', popularWords=popular)
		return output
	
	elif keywords is not None and keywords:		
		# We may need to do some search
		print 'keywords:', keywords
		# tokenize keywords 
		currentKeywordList = keywords.split('=')
		print 'Current keywords after splitting ''='':', currentKeywordList
		currentKeywordList = currentKeywordList[1].split('+')
		# Split this one more time by ignoring all empty strings
		currentKeywordList = [w for w in currentKeywordList if w != '']
		current_dictionary = {}
		print 'NOW! Current keywords:', currentKeywordList
		
		# By this time, we should be done splitting for good
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
		# Just printing out some data on server side for debugging purposes
		print 'Dictionary is:', dictionary
		print 'sorted_dictionary is:', sorted_dictionary
		print 'current_dictionary is:', current_dictionary
		print '20 items:', popular
		# Need to display the current set of input keywords, and the count of those keywords
		output = template('make_table', wordList=current_dictionary, popularWords=popular)
		return output
	else:
		print 'In the else clause, nothing to do, just return home page'	
		output = template('empty_string_table', popularWords=popular)
		return output

run(host = 'localhost', port = 8080, debug = True)

