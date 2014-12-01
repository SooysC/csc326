import boto.ec2
import os
import time

AWS_ACCESS_KEY_ID = 'AKIAIDEMXREVBLQBP6ZA'
AWS_SECRET_ACCESS_KEY = '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'
KEY_NAME = 'key_pair_script'
PEM_PATH = './aws/'
SECURITY_GROUP_NAME = 'csc326-group25-scipt'
SECURITY_GROUP_DESC = 'security group 25 for csc326'
AMI = 'ami-8caa1ce4'



def connect_to_aws():
    return boto.ec2.connect_to_region("us-east-1", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def aws_init():
    conn = connect_to_aws()

    kp = conn.create_key_pair(KEY_NAME)
    os.system("rm -f %s" % PEM_PATH+KEY_NAME+'.pem')
    kp.save(PEM_PATH)

    sg = conn.create_security_group(SECURITY_GROUP_NAME, SECURITY_GROUP_DESC)

    conn.authorize_security_group(group_name=sg.name, ip_protocol='icmp', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
    conn.authorize_security_group(group_name=sg.name, ip_protocol='tcp', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
    conn.authorize_security_group(group_name=sg.name, ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')

    reservation_obj = conn.run_instances('ami-8caa1ce4', instance_type='t1.micro', security_groups=[sg.name], key_name=KEY_NAME)
    return (conn, reservation_obj.instances[0])


def setup_static_ip_address(conn, instance):
    address = conn.allocate_address()
    address.associate(instance_id = instance.id)
    return address


def get_instance_status(conn, instance_ids=None):
    instances = conn.get_all_instance_status(instance_ids=instance_ids)
    if not instances:
        return "none"
    else:
        return instances[0].system_status.status


def setup():
    conn, instance = aws_init()

    while (get_instance_status(conn, instance_ids=instance.id) != 'ok'):
        time.sleep(1)

    address = setup_static_ip_address(conn, instance)

    return (address.public_ip, instance.id, PEM_PATH+KEY_NAME+'.pem')


