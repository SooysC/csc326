import bottle
from bottle import route, run, get, post, request, template, debug, static_file, TEMPLATE_PATH
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets 
from googleapiclient.errors import HttpError 
from googleapiclient.discovery import build
import json
import operator
import httplib2
from beaker.middleware import SessionMiddleware
import sqlite3 as lite
import os

session_opts = {
	    'session.type': 'file',
	    'session.cookie_expires': 300,
	    'session.data_dir': './data',
	    'session.auto': True
}


results_page_template = """
<!DOCTYPE html>
<html>
<body>

<h1>Ding</h1>

<h4>Results</h4>

<table border="1" id="results">
%for key, value in enumerate(url_list):
    <tr>
        <td>{{key}} </td>
        <td>{{value}} </td>
    </tr>	
%end
</table>


<form name="" method="get" action="">  
  <input type="submit" name="next" value="True"/>
</form>

</body>
</html>
"""

url_file = open('dummy_url_list.txt')
url_list = []
app = SessionMiddleware(bottle.app(), session_opts)

@route('/results')
def displayResults():
	print 'displayResults......'

@route('/', method = 'GET')
def processQuery():

	urlparams = request.query_string
	print 'urlparams--->', urlparams
	
	query = urlparams.split('=')
	# Index 0 is queryType, and Index 1 is queryParams
	queryType = query[0]
	queryParams = query[1]

	
	for line in url_file: 
		url_list.append(line)
    	#print line
	#print '---url_list----'
	#print url_list

	# do pagination here
	path = os.getcwd()
	if not os.path.exists(path):
		os.makedirs(path)

	current_results_page = 1
	# get number of results
	num_results = len(url_list)
	if num_results != 0:
		num_results_pages = num_results / 10;
		# for all the extra results	
		if num_results % 10 > 0:
			num_results_pages = num_results_pages + 1		
			
		for i in range(1, num_results_pages + 1):
			filename = 'results_page_' + str(i) +'.tpl'
			with open(os.path.join(path, filename), 'wb') as temp_file:
				temp_file.write(results_page_template)
			
	# http://localhost:8080/?next=True
	'''
	IDEA: Create one type of results tpl file, and then keep returning that 
		  based on which results_page was asked for, and slice the list in that way 
		  to only display that range of results
	'''
	if queryType == "next" and queryParams == "True":
		#bottle.redirect('/results')
		# navigate to next results page
		if(current_results_page != num_results_pages):
			tplfile = 'results_page' + str(current_results_page + 1)
			output = template(  tplfile, 
								url_list = url_list
					 	 	 )
	else:
		tplfile = 'results_page' + str(current_results_page)
		output = template(  tplfile, 
							url_list = url_list
					 	 )
	return output
run(app = app, host = 'localhost', port = 8080, debug = True)