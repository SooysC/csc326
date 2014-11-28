import bottle
from bottle import debug, error, get, post, request, response, route, run, static_file, template, TEMPLATE_PATH

from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

import json
import operator
from beaker.middleware import SessionMiddleware
import sys
sys.path.insert(0, '../crawler/')
sys.path.insert(0, './lib/')
import crawler_db
import env_server
import google_authenticator

TEMPLATE_PATH.insert(0,'./views/')

# GLOBAL
sorted_url_list = []
num_pages = 0
page_num = 1
urls_per_page = 10
search_history = {}

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
    bottle.redirect('/') # fix this - Erik


@route('/search', method = 'POST')
def search():
    words = request.forms.get('words')
    page_num = int(request.forms.get('page_num'))
    sorted_url_list = crawler_db.get_all_sorted_urls(words)

    if len(sorted_url_list) == 0:
        output = template( 'no_search_results', words = words)
    else:
        output = template( 'search_results',
                url_list = sorted_url_list[(page_num - 1) * urls_per_page : (page_num - 1) * urls_per_page + urls_per_page],
                page_num = page_num,
                list_size = len(sorted_url_list)
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
def processQuery():
    # get session
    session = request.environ.get('beaker.session')
    global sorted_url_list
    global page_num
    global num_pages
    keywords =  request.query_string
    urlparams = request.query_string
    if urlparams == "":
        # return the home page
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
            flow = flow_from_clientsecrets('client_secrets.json',
                    scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
                    # redirect_uri = 'http://localhost:8080/oauth2callback'
                    redirect_uri='http://ec2-54-173-22-59.compute-1.amazonaws.com/oauth2callback'
                    )
            uri = flow.step1_get_authorize_url()
            bottle.redirect(str(uri))
        # http://localhost:8080/?signOutButton=signOut
        if queryType == "signOutButton" and queryParams == "signOut":
            # We need to sign out
            session.delete()
            #bottle.redirect('https://accounts.google.com/logout')
            bottle.redirect('/')
        # Search queries go here
        if queryType == "keywords":
            # We may need to do some search
            currentKeywordList = queryParams.split('+')
            # Split this one more time by ignoring all empty strings
            currentKeywordList = [w for w in currentKeywordList if w != '']

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
                # signed up mode
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
                sorted_url_list = crawler_db.get_all_sorted_urls(first_word)


                num_pages = len(sorted_url_list) / urls_per_page
                if len(sorted_url_list) % urls_per_page != 0:
                    num_pages = num_pages + 1

                output = template( 'search_results',
                        url_list = sorted_url_list[:urls_per_page],
                        page_num = page_num,
                        list_size = len(sorted_url_list),
                        num_pages = num_pages,
                        user_email = user_email
                        )
                return output
            else:
                ##### not signed in, user_email should not be referenced
                # anon mode
                anon_results = {}
                for word in currentKeywordList:
                    if word in anon_results:
                        anon_results[word] = anon_results[word] + 1
                    else:
                        anon_results[word] = 1
                # Need to display the current set of input keywords, and the count of those keywords
                #output = template('anon_results', wordList = anon_results, user_email = '')
                sorted_url_list = crawler_db.get_all_sorted_urls(first_word)

                num_pages = len(sorted_url_list) / urls_per_page
                if len(sorted_url_list) % urls_per_page != 0:
                    num_pages = num_pages + 1

                # At this point, return first ten results only

                output = template(	'search_results',
                        url_list = sorted_url_list[:urls_per_page],
                        page_num = page_num,
                        list_size = len(sorted_url_list),
                        num_pages = num_pages,
                        user_email = ''
                        )
                return output
        if queryType == "next":
            page_num = page_num + 1

            try:
                email = session['user_email']
            except:
                email = ''

            if page_num <= num_pages:
                output = template(	'search_results',
                        url_list = sorted_url_list[(page_num - 1) * urls_per_page : (page_num - 1) * urls_per_page + urls_per_page],
                        page_num = page_num,
                        list_size = len(sorted_url_list),
                        num_pages = num_pages,
                        user_email = email
                        )
                return output
        if queryType == "prev" and page_num > 0:
            page_num = page_num - 1

            try:
                email = session['user_email']
            except:
                email = ''

            if page_num > 0:
                output = template( 'search_results',
                        url_list = sorted_url_list[(page_num - 1) * urls_per_page : (page_num - 1) * urls_per_page + urls_per_page],
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

