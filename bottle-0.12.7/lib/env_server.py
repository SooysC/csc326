import socket

IP_ADDRESSES_FOR_AWS = ['172.31.32.183', '172.31.33.215']

def current_ip():
    return socket.gethostbyname(socket.gethostname())

def is_aws():
    return current_ip() in IP_ADDRESSES_FOR_AWS

def client_secret_file():
    if is_aws():
        return "client_secret_%s.json" % current_ip()
    else:
        return "client_secret_localhost.json"
