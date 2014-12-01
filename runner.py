import os

PIP_MODULES = ['beaker','fuzzywuzzy','boto','oauth2client','google-api-python-client','BeautifulSoup']

def run():
    os.system('sudo python csc326/get-pip.py')

    for module in PIP_MODULES:
        os.system('sudo pip install %s' % module)

    os.chdir('csc326/bottle-0.12.7')

    os.system('screen -dm sudo python feServer.py')

run()
