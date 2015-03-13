#!/usr/bin/env python
__author__ = 'nbaker'
import json
import urllib
import urllib2
import os
import commands
import sys
import re
import logging
#from base64 import encodestring
import base64

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

if (len(sys.argv) < 2):
    logging.error("backup location not specified")
    sys.exit(-1)

logging.info('Starting backup')
#backup_location = os.getenv('HOME') + "/temp/backups"
backup_location = sys.argv[1]
logging.info("backup_location: "+backup_location)

try:
    if not os.path.exists(backup_location):
    os.makedirs(backup_location)


    username="buildguy"
    password = "S6ddxtky"

    #url = 'https://api.github.com/orgs/pentaho/repos'

    print "before while"
    nextURL = 'https://api.github.com/orgs/pentaho/repos'
    allRepos = []
    while nextURL is not None:
        print nextURL


    request = urllib2.Request(nextURL)
    #request.add_header('Authorization', 'Basic %s' % "cGVudGFob2FkbWluOnp6MXFTR1ZH".replace('\n', ''))

    request.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    url = urllib2.urlopen(request)


    # detect pagination
    link = url.info().getheader("link")
    if link is not None:
        m = re.search('<([^>]+)>; rel="next"', link)
        if m:
            nextURL = m.group(1)
        else:
            nextURL = None
    else:
        nextURL = None

    data = url.read()
    repos = json.loads(data);
    # print repos
    for r in repos:
        allRepos.append(r)

    for r in allRepos:
        name = r['name']
        url = "git@github.com:%s.git" % r['full_name']
        logging.info(url)


    repoLocation = backup_location + os.sep + name;

    if not os.path.exists(repoLocation):
        logging.info('cloning: ' + name)
        result = commands.getoutput('git clone --bare ' +url + ' ' + repoLocation)
        logging.info('output => '+result)
    else:
        logging.info('fetching: ' + name)
        os.chdir(repoLocation)
        result = commands.getoutput('git fetch origin')
        os.chdir(backup_location)
        logging.info('output => '+result)


        logging.info('Backup Complete')
except Exception as e:
    logging.error('Error encountered in backup: ' + e.message)
    sys.exit(-1)

sys.exit(-1)
