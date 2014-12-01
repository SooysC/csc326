import socket
from boto.utils import get_instance_metadata

IP_ADDRESSES_FOR_AWS = ['172.31.32.183', '172.31.33.215']

def current_ip():
    return socket.gethostbyname(socket.gethostname())

def is_aws():
    return len(get_instance_metadata(timeout=2, num_retries=2).keys()) > 0

def client_secret_file():
    if current_ip() in IP_ADDRESSES_FOR_AWS:
        return "client_secret_%s.json" % current_ip()
    else:
        return "client_secret_localhost.json"
