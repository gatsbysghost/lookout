#!/usr/bin/env python3

#author: Scott Reu (sreu@cisco.com)

import os
import time
import re
import datetime

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


#password = urllib.quote_plus('reu$db')
#MongoClient('mongodb://mongoAdmin:SourceFirePower@127.0.0.1')
#MongoClient('127.0.0.1', 27017)

client = MongoClient()
db = client.fmcDB
db.authenticate('lookout','HashBangFP')
canaries = db.canaries
coalmine = db.coalmine

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
        result = ('STATUS FOR FMC/CANARY '+self.hostname+' ('+self.ipaddr+'): '+self.status)
        if self.status == 'fail':
            result += (', failure code: ')
            if self.failcode != '':
                result += self.failcode
            else:
                result += 'n/a'
        return result

    def __init__(self, hostname=None, ipaddr=None, username='', passwd='', status='init', failcode=''):
        self.hostname = hostname
        self.ipaddr = ipaddr
        self.username = username
        self.passwd = passwd
        #Possible statuses: 'init', 'ok', 'fail'
        self.status = status
        self.failcode = failcode

def cloudStatus():
    '''
    Initialize some counters.
    For every FMC in our python data structure, increment the 'ok' counter if the device has an 'ok' status
    likewise increment the 'fail' counter if the device has a 'fail' status.
    If there is exactly one monitored FMC, return that FMC's status (str) as the global status.
    Else, if there is more than one monitored FMC,
            if 2 or more boxes have failed, return 'fail' as the global status.
            if 0 or 1 boxes have failed, return 'ok' as the global status.
    '''
    okCount = 0
    failCount = 0
    otherCount = 0
    for fmc in lookoutlist.fmclist:
        if fmc.status == 'ok':
            okCount += 1
        elif fmc.status == 'fail':
            failCount += 1
        else:
            otherCount += 1
    if (okCount + failCount + otherCount) == 1:
        if failCount == 1:
            return 'fail'
        elif okCount == 1:
            return 'ok'
        else:
            return 'init'
    elif (okCount + failCount + otherCount) > 1:
        if failCount >= 2:
            return 'fail'
        else:
            return 'ok'

def updateCanary(fmc):
    '''
    Given an Fmc object as input:
    Find the entry in the fmcDB, in the canaries collection, with that object's hostname
    Set that database's "status" field to the current status of the Fmc object.
    '''
    result = canaries.update_one(
        {"hostname": fmc.hostname},
        {
            "$set": {
                "status": fmc.status,
                "failcode":fmc.failcode
            },
            "$currentDate": {"lastModified": True}
        }
    )
    return result

def updateCoalmine():
    '''
    Update the Coalmine collection in the fmcDB (mongoDB)
    Find the member with the name "Global" (the only thing in this collection)
    Set the status to the result of cloudStatus().
    '''
    result = coalmine.update_one(
        {'name': 'global'},
        {
            "$set": {
                "status": cloudStatus()
            }
        }
    )

def main():
    '''
    While true, check whether there has been a known "OK" CloudAgent log since the last time we checked.
    Check whether there has been a known "Fail"-condition CloudAgent log since the last time we checked.
    If one of these has been detected, and it's more recent than a log of the other type (e.g.,
    if we get a fail log and it's occurred more recently than an OK log, or vice versa), then
    update the FMC's status parameter to reflect the current status.
    
    Then, evaluate the status of Brightcloud in general based on how many of our test boxes have failed.
    '''
    os.chdir('/home/support/lookoutLog')
    #canaries.drop()
    #coalmine.drop()
    for fmc in lookoutlist.fmclist:
        found = canaries.find({'hostname':fmc.hostname})
        if found.count() == 0:
            result = canaries.insert_one(
            {
                'hostname': fmc.hostname,
                'ipaddr': fmc.ipaddr,
                'status': fmc.status,
                'failcode': fmc.failcode
            }
            )
    globfound = coalmine.find({'name':'global'})
    if globfound.count() == 0:
        result = coalmine.insert_one(
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
                        #match = re.search('CloudAgent:IPReputation \[WARN\] Download unsucessful: Timeout was reached')
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
                            time.sleep(5)
                    else:
                        if len(goodIndex) > 0:
                            if len(badIndex) == 0:
                                if fmc.status == 'fail' or fmc.status == 'init':
                                    fmc.ok()
                                    updateCanary(fmc)
                            else:
                                if int(goodIndex[-1]) > int(badIndex[-1]):
                                    if fmc.status == 'fail' or fmc.status == 'init':
                                        fmc.ok()
                                        updateCanary(fmc)
                                    #print('Marking FMC '+fmc.hostname+' OK.')
                                else:
                                    match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',temp[badIndex[-1]])
                                    code = match.group(3)
                                    if fmc.status == 'ok' or fmc.status == 'init':
                                        fmc.fail(code)
                                        updateCanary(fmc)
                                    elif fmc.status == 'fail':
                                        if fmc.failcode != code:
                                            fmc.fail(code)
                                            updateCanary(fmc)
                                    #print('Marking FMC '+fmc.hostname+' Failed.')
                        else:
                            match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',temp[badIndex[-1]])
                            code = match.group(3)
                            if fmc.status == 'ok' or fmc.status == 'init':
                                fmc.fail(code)
                                updateCanary(fmc)
                            elif fmc.status == 'fail':
                                if fmc.failcode != code:
                                    fmc.fail(code)
                                    updateCanary(fmc)
                            #print('Marking FMC '+fmc.hostname+' Failed.')
                        time.sleep(5)
            else:
                #print("Didn't find a log! waiting 5")
                time.sleep(5)
            with open('lookout.log','a') as g:
                g.write('['+str(datetime.datetime.now())+'] (lookout)\n')
                g.write(fmc.debug())
                g.write('\n')
        for fmc in lookoutlist.fmclist:
            with open('lookout.log','a') as g:
                g.write('['+str(datetime.datetime.now())+'] (lookout)\n')
                g.write(fmc.debug())
                g.write('\n')
        lookoutweb.updateHTML()
        updateCoalmine()
        with open('lookout.log','a') as g:
                g.write('['+str(datetime.datetime.now())+'] (lookout) OVERALL (COALMINE) STATUS: '+cloudStatus())
        #
        # Debug DB:
        #
        #fmccursor = canaries.find()
        #print('\nDEBUG: FMCs currently in DB:\n\n')
        #for document in fmccursor:
        #    print(document)
        #globcursor = coalmine.find()
        #print('\nDEBUG: Global status currently in DB:\n\n')
        #for document in globcursor:
        #    print(document)
        
if __name__ == '__main__':
    main()
