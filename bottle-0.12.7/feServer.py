import bottle
from bottle import debug, error, get, post, request, response, route, run, static_file, template, TEMPLATE_PATH
import json
import operator
from beaker.middleware import SessionMiddleware
import sys
sys.path.insert(0, './lib/')
import crawler_db
import env_server
import google_authenticator

TEMPLATE_PATH.insert(0,'./views/')

# GLOBAL
URLS_PER_PAGE = 10

session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
        }
app = SessionMiddleware(bottle.app(), session_opts)


@error(404)
def error404(error):
    output = template('error_page')
    return output


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Static Routes
@route('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/javascript')

@route('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@route('/<filename:re:.*\.css.map>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@route('/<filename:re:.*\.(jpg|jpeg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='static/image')

@route('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return static_file(filename, root='static/fonts')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@route('/oauth2callback')
def redirect_page():
    s = request.environ.get('beaker.session') # Create a beaker session
    s['user_email'] = google_authenticator.get_user_email(request)
    s.save()
    bottle.redirect('/')


@route('/search', method = 'POST')
def search():
    words = request.forms.get('words')
    page_num = int(request.forms.get('page_num'))
    recommended_words, sorted_url_list = crawler_db.get_all_sorted_urls(words)

    if len(sorted_url_list) == 0:
        output = template( 'no_search_results', words = words, recommended_words = recommended_words)
    else:
        output = template( 'search_results',
                url_list = sorted_url_list[(page_num - 1) * URLS_PER_PAGE : (page_num - 1) * URLS_PER_PAGE + URLS_PER_PAGE],
                page_num = page_num,
                list_size = len(sorted_url_list),
                recommended_words = recommended_words
                )
    return output;


@route('/signin', method = 'GET')
def signIn():
   uri = google_authenticator.get_uri()
   bottle.redirect(str(uri))


@route('/signout', method = 'GET')
def signOut():
   session = request.environ.get('beaker.session')
   session.delete()
   bottle.redirect('/')


@route('/', method = 'GET')
def mainPage():
    session = request.environ.get('beaker.session')

    try:
        email = session['user_email']
    except:
        email = ''
    output = template('homepage', user_email = email)
    return output


if (env_server.is_aws()):
    run(app = app, host='0.0.0.0', port = 80) # for AWS EC2
else:
    run(app = app, host = 'localhost', port = 8080, debug = True)

