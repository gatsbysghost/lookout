#!/usr/bin/env python3

#author: Scott Reu (sreu@cisco.com)

import os
import time
import re

from pymongo import MongoClient

import lookoutlist
import lookoutweb


'''
1) Use TaSc to cat /var/log/messages on each FMC we specify
2) While true:
    2a) For each FMC's logfile:
        (tasc will be responsible for ensuring that only one exists at a time)
        2c) With that file open:
            2d) Regex search to find the most recent CloudAgent logs:
                    -Possibility 1) We see CloudAgent failure logs with no success afterward;
                    -Possibility 2) We see CloudAgent success logs with no failure logs afterward;
                2e) If (1) is the case, update that FMC's status to "fail". Else,
                    update that FMC's status to "ok".
3) If n > 1 of the FMCs have a status of "fail", update the HTML to the Failed page.
    Else, update the HTML to the OK page.
'''

client = MongoClient()
db = client.fmcDB
collection1 = db.canarydb
collection2 = db.coalminedb

class Fmc(object):
    '''
    A class for FMCs in the lookout framework (to make it easier to reference
    IPs and hostnames and to provide methods for tracking various kinds of
    device statuses).
    '''

    def fail(self, failcode=''):
        '''
        '''
        self.status = 'fail'
        self.failcode = failcode
        

    def ok(self):
        '''
        '''
        self.status = 'ok'
        self.failcode = ''
        
    def debug(self):
        print('------FMC DEBUG------\n')
        print('Hostname: '+self.hostname+'\n')
        print('IP Addr: '+self.ipaddr+'\n')
        print('Status: '+self.status+'\n')
        if self.status == 'fail':
            print('Failure code: '+self.failcode+'\n')
        print('----------------------')

    def __init__(self, hostname=None, ipaddr=None, username='', passwd='', status='ok', failcode=''):
        self.hostname = hostname
        self.ipaddr = ipaddr
        self.username = username
        self.passwd = passwd
        self.status = status
        self.failcode = failcode

def cloudStatus():
    okCount = 0
    failCount = 0
    for fmc in lookoutlist.fmclist:
        if fmc.status == 'ok':
            okCount += 1
        elif fmc.status == 'fail':
            failCount += 1
    if (okCount + failCount) == 1:
        if failCount == 1:
            return 'fail'
        else:
            return 'ok'
    elif okCount + failCount > 1:
        if failCount >= 2:
            return 'fail'
        else:
            return 'ok'

def main():
    '''
    '''
    os.chdir(os.path.join(os.path.expanduser('~'), 'lookoutLog'))
    collection1.drop()
    collection2.drop()
    for fmc in lookoutlist.fmclist:
        found = collection1.find({'hostname':fmc.hostname})
        if found.count() == 0:
            result = collection1.insert_one(
            {
                'hostname': fmc.hostname,
                'ipaddr': fmc.ipaddr,
                'status': fmc.status,
                'failcode': fmc.failcode
            }
            )
    globfound = collection2.find({'name':'global'})
    if globfound.count() == 0:
        result = collection2.insert_one(
            {
                'name': 'global',
                'status': 'ok'
            }
            )
    while True:
        for fmc in lookoutlist.fmclist:
            logname = fmc.hostname+'.log'
            if os.path.isfile(logname):
                with open(logname,'r') as log:
                    temp = []
                    for line in log:
                        temp.append(line)
                    goodIndex = []
                    badIndex = []
                    for line in temp:
                        match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',line)
                        if match != None:
                            # We can record the most recent failcode on the box like this:
                            badIndex.append(temp.index(line))
                        match = re.search('CloudAgent \[INFO\] Nothing to do, database is up to date', line)
                        if match != None:
                            goodIndex.append(temp.index(line))
                        match = re.search('CloudAgent \[INFO\] Calling URL Filtering DB synchronization perl transaction', line)
                        if match != None:
                            goodIndex.append(temp.index(line))
                    goodIndex.sort()
                    badIndex.sort()
                    # if there's both a bad match and a good match, get the highest index on which we match
                    # from both goodlist and badlist
                    # so in essence, our condition is just whether goodlist[-1] < badlist[1]
                    if len(goodIndex) == 0:
                        if len(badIndex) == 0:
                            fmc.debug()
                            time.sleep(5)
                    else:
                        if len(goodIndex) > 0:
                            if len(badIndex) == 0:
                                fmc.ok()
                            else:
                                if int(goodIndex[-1]) > int(badIndex[-1]):
                                    fmc.ok()
                                    #print('Marking FMC '+fmc.hostname+' OK.')
                                else:
                                    match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',temp[badIndex[-1]])
                                    code = match.group(3)
                                    fmc.fail(code)
                                    #print('Marking FMC '+fmc.hostname+' Failed.')
                        else:
                            match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',temp[badIndex[-1]])
                            code = match.group(3)
                            fmc.fail(code)
                            #print('Marking FMC '+fmc.hostname+' Failed.')
                        fmc.debug()
                        time.sleep(5)
            else:
                #print("Didn't find a log! waiting 5")
                time.sleep(5)
        lookoutweb.updateHTML()
        for fmc in lookoutlist.fmclist:
            result = collection1.update_one(
                {"hostname": fmc.hostname},
                {
                    "$set": {
                        "status": fmc.status
                    },
                    #"$currentDate": {"lastModified": True}
                }
            )
        result = collection2.update_one(
                {'name': 'global'},
                {
                    "$set": {
                        "status": cloudStatus()
                    }
                }
        )
        fmccursor = collection1.find()
        print('\nDEBUG: FMCs currently in DB:\n\n')
        for document in fmccursor:
            print(document)
        globcursor = collection2.find()
        print('\nDEBUG: Global status currently in DB:\n\n')
        for document in globcursor:
            print(document)
        
if __name__ == '__main__':
    main()
