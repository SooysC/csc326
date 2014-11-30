import boto.ec2
import sys

sys.path.insert(0, './aws/')
import aws_setup


#Public IP Address: 54.173.28.171
#Instance ID: i-e6164507

def terminate(instance_id):
    if not instance_id:
        print "Please provide the instance_id by 'python terminator.py instance_id'"
        return None
    conn = aws_setup.connect_to_aws()
    conn.terminate_instances(instance_ids=[instance_id])

    if (aws_setup.get_instance_status(conn, [instance_id]) == 'none'):
        print "Termination of Instance %s is successful." % instance_id
    else:
        print "Termination of Instance %s failed." % instance_id


if len(sys.argv) == 2:
    terminate(sys.argv[1])
else:
    terminate(None)
