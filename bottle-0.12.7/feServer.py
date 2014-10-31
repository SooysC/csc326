import bottle
from bottle import route, run, get, post, request, template, debug, static_file, TEMPLATE_PATH
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets 
from googleapiclient.errors import HttpError 
from googleapiclient.discovery import build
import json
import operator
import httplib2
from beaker.middleware import SessionMiddleware

TEMPLATE_PATH.insert(0,'./')

search_history = {}
current_user_history = {}
recent = []

s = None
session_opts = {
	    'session.type': 'file',
	    'session.cookie_expires': 300,
	    'session.data_dir': './data',
	    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

@route('/oauth2callback') 
def redirect_page():
	code = request.query.get('code', '')

	with open("client_secrets.json") as json_file:
		client_secrets = json.load(json_file)
		CLIENT_ID = client_secrets["web"]["client_id"]		
		CLIENT_SECRET = client_secrets["web"]["client_secret"]
		SCOPE = client_secrets["web"]["auth_uri"]
		REDIRECT_URI = client_secrets["web"]["redirect_uris"]
	
	flow = OAuth2WebServerFlow(client_id = '547843285800-lr7jojdv25gec092j0aqlc205m35bl2k.apps.googleusercontent.com', 
                            client_secret = 'WOgP3CpvfEsQ_epZpHa_g2D5', 
                            scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', 
                            redirect_uri = 'http://localhost:8080/oauth2callback') 
	
	
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub'] 
	http = httplib2.Http() 
	http = credentials.authorize(http) 			
	# Get user email 
	users_service = build('oauth2', 'v2', http = http) 
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']

	# Create a beaker session
	global s
	s = request.environ.get('beaker.session')
	s['user_email'] = user_email
	s.save()
	bottle.redirect('/')

@route('/', method = 'GET')
def processQuery():
	print 'processQuery'
	keywords =  request.query_string
	urlparams = request.query_string
	print 'urlparams--->', urlparams

	if urlparams == "":
		# return the home page
		print 'Gonna return the home page'
		output = template('homepage')
		return output
	# The URL params contain something, distinguish if it's a search or a sign in
	elif urlparams is not None and urlparams:
		query = urlparams.split('=')
		# Index 0 is queryType, and Index 1 is queryParams
		queryType = query[0]
		queryParams = query[1]

		# http://localhost:8080/?signInButton=signIn
		if queryType == "signInButton" and queryParams == "signIn":
			# We need to sign in
			print "Signin............"
			# TODO Eventually we should return a tpl file with the proper layout, but forget that for now
			flow = flow_from_clientsecrets('client_secrets.json', 
											scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', 
											redirect_uri='http://localhost:8080/oauth2callback')
			uri = flow.step1_get_authorize_url() 
			#print uri
			bottle.redirect(str(uri)) 
		# http://localhost:8080/?signOutButton=signOut
		if queryType == "signOutButton" and queryParams == "signOut":
			# We need to sign out
			print 'signOut..........'
			s.delete()
			#bottle.redirect('https://accounts.google.com/logout')
			bottle.redirect('/')
		if queryType == "keywords":			
			# We may need to do some search
			currentKeywordList = queryParams.split('+')
			# Split this one more time by ignoring all empty strings
			currentKeywordList = [w for w in currentKeywordList if w != '']
			print 'Current keywords:', currentKeywordList
			
			# Determine signed up mode vs anon mode		
			try:
				user_email = s['user_email']
				print 'User email is:', user_email
				# signed up mode
				print 'signed up mode...........'
				current_user_results = {}
				global search_history, current_user_history, recent
				#print 'Before all recent', recent
				for word in currentKeywordList:
					if word in current_user_results:
						current_user_results[word] = current_user_results[word] + 1
					else:
						current_user_results[word] = 1

				for word in currentKeywordList:
					recent.append(word)

				print 'current user results', current_user_results				

				if recent is None:
					print 'recent is empty'
				if len(recent) < 10:
					#print 'recent', recent
					most_recent = recent[:len(recent)]
					#print 'less than 10'
				else:
					most_recent = recent[-10:]
					#print 'more than 10'
				print 'most_recent:', most_recent
				search_history[user_email] = [current_user_results, most_recent]
				print '_' * 10
				print 'Search History:'
				print '_' * 10
				print search_history
				print '_' * 10

				output = template( 'signed_in_results', 
									wordList = search_history[user_email][0], #dict 
									popularWords = search_history[user_email][1] #list
								 )
				return output
			except:
				# anon mode
				print 'Anon mode........'
				anon_results = {}
				for word in currentKeywordList:
					if word in anon_results:
						anon_results[word] = anon_results[word] + 1
					else:
						anon_results[word] = 1
				# Need to display the current set of input keywords, and the count of those keywords
				output = template('anon_results', wordList=anon_results)
				return output
	else:
		print 'In the else clause, nothing to do, just return home page'
		output = template('homepage')
		return output

run(app = app, host = 'localhost', port = 8080, debug = True)
#run(host='0.0.0.0', port = 80) # for AWS EC2
