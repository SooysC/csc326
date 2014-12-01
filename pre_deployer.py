import os

def setup_for_deployment():
    os.system('git clone git://github.com/boto/boto.git')
    os.chdir('boto')
    os.system('python setup.py install --user')
    os.chdir('..')
    os.system('python deployer.py')

setup_for_deployment()
