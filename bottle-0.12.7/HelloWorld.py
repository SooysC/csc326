from bottle import route, run
from bottle import static_file

@route('/')
def hello():
  #return "<h1>Hello World<h1>"
  filename = "index.html"
  return static_file(filename, root='../html/')
run(host='localhost', port=8080, debug=True)

