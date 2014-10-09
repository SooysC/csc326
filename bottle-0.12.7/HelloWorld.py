from bottle import route, run
from bottle import static_file
from bottle import get, post, request
@route('/', method = 'POST')
def processQuery():
	postdata = request.json
	print postdata
	return "postdata" # not exactly working
@route('/', method = 'GET')	
def hello():
	filename = "index.html"
	return static_file(filename, root='../html/')
run(host = 'localhost', port = 8080, debug = True)

