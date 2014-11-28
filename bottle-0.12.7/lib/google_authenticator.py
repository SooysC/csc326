from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import json
import httplib2
import env_server

with open(env_server.client_secret_file()) as json_file:
    client_secrets = json.load(json_file)
    CLIENT_ID = client_secrets["web"]["client_id"]
    CLIENT_SECRET = client_secrets["web"]["client_secret"]
    SCOPE = client_secrets["web"]["auth_uri"]
    REDIRECT_URI = client_secrets["web"]["redirect_uris"][0]
GOOGLE_SCOPE = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'


def get_user_email(request):
    flow = OAuth2WebServerFlow(client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET,
            scope = GOOGLE_SCOPE,
            redirect_uri = REDIRECT_URI
            )
    code = request.query.get('code', '')
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']
    http = httplib2.Http()
    http = credentials.authorize(http)
    users_service = build('oauth2', 'v2', http = http)
    user_document = users_service.userinfo().get().execute()
    return user_document['email']


def get_uri():
    flow = flow_from_clientsecrets(env_server.client_secret_file(),
            scope=GOOGLE_SCOPE,
            redirect_uri=REDIRECT_URI
            )
    return flow.step1_get_authorize_url()

