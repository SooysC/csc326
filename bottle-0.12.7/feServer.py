import bottle
from bottle import route, run, get, post, request, template, debug, static_file, TEMPLATE_PATH
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets 
from googleapiclient.errors import HttpError 
from googleapiclient.discovery import build
import json
import operator
import httplib2
from beaker.middleware import SessionMiddleware

# crawler db
import sys

sys.path.insert(0, '../crawler/')
import crawler_db

###################################### For Samprit:
# to get an array of urls, use:
# crawler_db.get_sorted_urls("word")
######################################


TEMPLATE_PATH.insert(0,'./')

search_history = {}

session_opts = {
	    'session.type': 'file',
	    'session.cookie_expires': 300,
	    'session.data_dir': './data',
	    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

from bottle import error
@error(404)
def error404(error):
	output - template('error_page')
	return output

@route('/oauth2callback') 
def redirect_page():
	code = request.query.get('code', '')
	with open("client_secrets.json") as json_file:
		client_secrets = json.load(json_file)
		CLIENT_ID = client_secrets["web"]["client_id"]		
		CLIENT_SECRET = client_secrets["web"]["client_secret"]
		SCOPE = client_secrets["web"]["auth_uri"]
		REDIRECT_URI = client_secrets["web"]["redirect_uris"]
	
	flow = OAuth2WebServerFlow(client_id = CLIENT_ID, 
                            client_secret = CLIENT_SECRET, 
                            scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', 
                            redirect_uri = 'http://localhost:8080/oauth2callback'
                            #redirect_uri = 'http://ec2-54-173-22-59.compute-1.amazonaws.com/oauth2callback'
                            ) 
	
	
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub'] 
	http = httplib2.Http() 
	http = credentials.authorize(http) 			
	# Get user email 
	users_service = build('oauth2', 'v2', http = http) 
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']

	# Create a beaker session
	s = request.environ.get('beaker.session')
	s['user_email'] = user_email
	s.save()
	bottle.redirect('/')
	# Just serve the signed_in_results page
	'''
	output = template( 'signed_in_results', 
						wordList = None, #dict 
						popularWords = None, #list
						user_email = user_email
					 )
	return output
	'''
# GLOBAL
sorted_url_list = []
num_pages = 0
page_num = 1
url_per_page = 3
@route('/', method = 'GET')
def processQuery():
	# get session
	session = request.environ.get('beaker.session')
	global sorted_url_list
	global page_num
	global num_pages
	print 'processQuery'
	keywords =  request.query_string
	urlparams = request.query_string
	print 'urlparams--->', urlparams
	if urlparams == "":
		# return the home page
		print 'Gonna return the home page'
		try:
			email = session['user_email']
		except:
			email = ''
		output = template('homepage', user_email = email)
		return output

	elif urlparams is not None and urlparams:
		query = urlparams.split('=')
		# Index 0 is queryType, and Index 1 is queryParams
		queryType = query[0]
		queryParams = query[1]
		print 'queryType--->', queryType
		# http://localhost:8080/?signInButton=signIn
		if queryType == "signInButton" and queryParams == "signIn":
			# We need to sign in
			print "Signin............"
			flow = flow_from_clientsecrets('client_secrets.json', 
											scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', 
											redirect_uri = 'http://localhost:8080/oauth2callback'
											#redirect_uri='http://ec2-54-173-22-59.compute-1.amazonaws.com/oauth2callback'
											)
			uri = flow.step1_get_authorize_url() 
			#print uri
			bottle.redirect(str(uri)) 
		# http://localhost:8080/?signOutButton=signOut
		if queryType == "signOutButton" and queryParams == "signOut":
			# We need to sign out
			print 'signOut..........'
			session.delete()
			#bottle.redirect('https://accounts.google.com/logout')
			bottle.redirect('/')
		# Search queries go here
		if queryType == "keywords":			
			# We may need to do some search
			currentKeywordList = queryParams.split('+')
			# Split this one more time by ignoring all empty strings
			currentKeywordList = [w for w in currentKeywordList if w != '']

			print 'Current keywords:', currentKeywordList
			first_word = ''

			if currentKeywordList:
				first_word = currentKeywordList[0]
			if first_word == '':
				# return home page, not current
				try:
					email = session['user_email']
				except:
					email = ''
				output = template('homepage', user_email = email)
				return output 
				
			# reset page number and total number of result pages for every new search
			page_num = 1
			num_pages = 0
			is_signed_in = 'user_email' in session
			if is_signed_in:
				user_email = session['user_email']

			if is_signed_in:
				##### user is signed in and user_email is the user's email
				print 'User email is:', user_email
				# signed up mode
				print 'signed up mode...........'
				current_user_results = {}
				global search_history
				for word in currentKeywordList:
					if word in current_user_results:
						current_user_results[word] = current_user_results[word] + 1
					else:
						current_user_results[word] = 1

				if user_email not in search_history:
					search_history.update({user_email:[]})

				for word in currentKeywordList:
					search_history[user_email].append(word)

				history = search_history[user_email][-10:]
				print 'first_word:', first_word
				sorted_url_list = crawler_db.get_sorted_urls(first_word)
				print 'URL LIST:'
				print sorted_url_list

								
				num_pages = len(sorted_url_list) / url_per_page
				if len(sorted_url_list) % url_per_page != 0:
					num_pages = num_pages + 1

				print 'page_num:', page_num
				print 'num_pages:', num_pages
				#print 'user_email:', user_email
				'''
				output = template( 'signed_in_results', 
									wordList = current_user_results, #dict 
									popularWords = history, #list
									user_email = user_email
								 )
				'''
				output = template(	'search_results', 
									url_list = sorted_url_list[:url_per_page],
									page_num = page_num, 
									list_size = len(sorted_url_list), 
									num_pages = num_pages,
									user_email = user_email
								)
				return output
			else:
				##### not signed in, user_email should not be referenced
				# anon mode
				print 'Anon mode........'
				anon_results = {}
				for word in currentKeywordList:
					if word in anon_results:
						anon_results[word] = anon_results[word] + 1
					else:
						anon_results[word] = 1
				# Need to display the current set of input keywords, and the count of those keywords
				#output = template('anon_results', wordList = anon_results, user_email = '')
				print 'first_word:', first_word
				sorted_url_list = crawler_db.get_sorted_urls(first_word)
				print 'URL LIST:'
				print sorted_url_list

				num_pages = len(sorted_url_list) / url_per_page
				if len(sorted_url_list) % url_per_page != 0:
					num_pages = num_pages + 1

				# At this point, return first ten results only
				print 'page_num:', page_num
				print 'num_pages:', num_pages

				output = template(	'search_results', 
									url_list = sorted_url_list[:url_per_page], 
									page_num = page_num, 
									list_size = len(sorted_url_list), 
									num_pages = num_pages,
									user_email = ''
								)
				return output
		if queryType == "next":
			print "Next....."
			print 'queryParams', queryParams
			page_num = page_num + 1
			print 'page_num:', page_num
			print 'num_pages:', num_pages
			
			try:
				email = session['user_email']
			except:
				email = ''
			if page_num <= num_pages:
				output = template(	'search_results', 
									url_list = sorted_url_list[(page_num - 1) * url_per_page : (page_num - 1) * url_per_page + url_per_page], 
									page_num = page_num, 
									list_size = len(sorted_url_list), 
									num_pages = num_pages,
									user_email = email
								)
				return output
		if queryType == "prev" and page_num > 0:
			print "prev....."				
			print 'queryParams', queryParams
			page_num = page_num - 1
			print 'page_num:', page_num
			print 'num_pages:', num_pages

			try:
				email = session['user_email']
			except:
				email = ''

			if page_num > 0:
				output = template(	'search_results', 
									url_list = sorted_url_list[(page_num - 1) * url_per_page : (page_num - 1) * url_per_page + url_per_page], 
									page_num = page_num, 
									list_size = len(sorted_url_list), 
									num_pages = num_pages,
									user_email = email
								)
				return output
		if queryType == "home":
			try:
				email = session['user_email']
			except:
				email = ''
			output = template('homepage', user_email = email)
			return output

	else:
		print 'In the else clause, nothing to do, just return home page'
		try:
			email = session['user_email']
		except:
			email = ''
		output = template('homepage', user_email = email)
		return output

run(app = app, host = 'localhost', port = 8080, debug = True)
#run(app = app, host='0.0.0.0', port = 80) # for AWS EC2
