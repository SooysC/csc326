import socket

IP_ADDRESS_AWS_SERVER = '172.31.32.183'


def is_aws():
    return socket.gethostbyname(socket.gethostname()) == IP_ADDRESS_AWS_SERVER

def client_secret_file():
    if is_aws():
        return "client_secret_aws.json"
    else:
        return "client_secret_localhost.json"
