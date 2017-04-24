#!/usr/bin/env python3

import os
import time
import re
from multiprocessing import Process

import tasc
from lookoutlist import fmclist

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

class Fmc(object):
    '''
    A class for FMCs in the lookout framework (to make it easier to reference
    IPs and hostnames and to provide methods for tracking various kinds of
    device statuses).
    '''

    def fail(self):
        '''
        '''
        self.status = 'fail'

    def ok(self):
        '''
        '''
        self.status = 'ok'

    def __init__(self, hostname=None, ipaddr=None, username='', passwd='', status='ok', failcode=''):
        self.hostname = hostname
        self.ipaddr = ipaddr
        self.username = username
        self.passwd = passwd
        self.status = status
        self.failcode = failcode

def main():
    '''
    '''
    os.chdir(os.path.join(os.path.expanduser('~'), 'lookoutLog'))
    while True:
        for fmc in fmclist:
            logname = fmc.hostname+'.log'
            if os.path.isfile(logname):
                with open(logname,'r') as log:
                    temp = log.split('\n')
                    goodIndex = []
                    badIndex = []
                    for line in temp:
                        match = re.search('(CloudAgent \[WARN\]) .* (Socket error\.) Status: (.+)',line)
                        if match != None:
                            fmc.failcode = match.group(3)
                            badIndex.append(temp.index(line))
                    # if there's both a bad match and a good match, get the highest index on which we match
                    # from both goodlist and badlist
                    # so in essence, our condition is just whether goodlist[-1] < badlist[1]
                    if blablabla:
                        fmc.fail()
                    else:
                        fmc.ok()
            else:
                time.sleep(5)

if __name__ == '__main__':
    Process(target=tasc.go()).start()
    Process(target=main()).start()
    