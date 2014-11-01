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
@route('/', method = 'GET')
def processQuery():
	# get session
	session = request.environ.get('beaker.session')

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
			session.delete()
			#bottle.redirect('https://accounts.google.com/logout')
			bottle.redirect('/')
		if queryType == "keywords":			
			# We may need to do some search
			currentKeywordList = queryParams.split('+')
			# Split this one more time by ignoring all empty strings
			currentKeywordList = [w for w in currentKeywordList if w != '']
			print 'Current keywords:', currentKeywordList
			

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

				output = template( 'signed_in_results', 
									wordList = current_user_results, #dict 
									popularWords = history, #list
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


				output = template('anon_results', wordList = anon_results, user_email = '')
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
#run(host='0.0.0.0', port = 80) # for AWS EC2
