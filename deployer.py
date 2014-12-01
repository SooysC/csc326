import sqlite3 as lite
import os
import sys
sys.path.insert(0, './aws/')
sys.path.insert(0, './crawler/')

import aws_setup
import crawler

DB_FILE = "./crawler/dbFile.db"
URLS_TXT_FILE = "./crawler/urls.txt"


def deploy():

    # run crawler
    os.system("rm -f %s" % DB_FILE)
    db_conn = lite.connect(DB_FILE)
    bot = crawler.crawler(db_conn, URLS_TXT_FILE)
    bot.crawl(depth=1)
    print "Crawler Finished"  #change to decorator

    # aws setup
    print "Please wait while we are creating the instance"
    public_ip, instance_id, key_pair_path = aws_setup.setup()
    print "AWS Setup Finished"

    # scp
    os.system("rm -f ./bottle-0.12.7/data/") # delete cache for faster scp
    os.system("scp -r -o StrictHostKeyChecking=no -i %s ../csc326/ ubuntu@%s:~/" % (key_pair_path, public_ip))
    os.system("ssh -o StrictHostKeyChecking=no -i %s ubuntu@%s nohup python csc326/runner.py" % (key_pair_path, public_ip))
    print "App Launched"

    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Public IP Address: %s" % public_ip
    print "Instance ID: %s" % instance_id
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    return public_ip


deploy()


