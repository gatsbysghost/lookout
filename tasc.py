#!/usr/bin/env python3

#suthor: Scott Reu (sreu@cisco.com)

import sys # for the big red 'terminate' button
import time # for waiting
import os, os.path #for creating the logging fsys
import datetime # for getting system time

import paramiko # ssh methods

import lookoutlist

#
# GLOBAL VARIABLES
#
# Logging File Setup
# Delete any files in the logging directory
logloc = os.path.expanduser('~')
os.chdir('/home/support/lookoutLog')
for anyfile in os.listdir(logloc):
    path = os.path.join(logloc, anyfile)
    try:
        if os.path.isfile(path):
            os.unlink(path)
    except Exception as e:
        print(str(e))

def newLog(target):
    logfilename = target.hostname+'.log'
    logger = open(logfilename,'a')
    return logger

def rmLog(target):
    logfilename = target.hostname+'.log'
    if os.path.isfile(logfilename):
        os.remove(logfilename)

def ssh(target):
    '''
    Input: IP address (string), username (string), password (string), enable password (string),
    list of commands to run (list), device type (string), are we running a debug command? (boolean),
    are we logging SSH verbosely? (boolean), ssh dest port(int), value for calculating progressbar time (int).
    Action: Log into an ASA, run commands, log commands, log out of ASA. If a debug command was run,
    then at the end of the session we need to undebug all.
    Output: Debug output to terminal, main output written to logfile.
    '''
    # Create instance of SSHClient object
    run = paramiko.SSHClient()
    # Automatically add untrusted host keys
    run.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # initiate SSH connection
    try:
        run.connect(target.ipaddr, username=target.username, password=target.passwd, look_for_keys=False, allow_agent=False)
    except Exception as e:
        with open('lookout.log','a') as g:
                g.write('['+str(datetime.datetime.now())+'] (tasc) ')
                g.write('SSH ERROR: Check credentials and target IP address, and verify that the target is configured to allow SSH access from this host.\n'+str(e)+'\n')
#        target.status = 'notconnect'
        pass
    stdin, stdout, stderr = run.exec_command(('\ncat /var/log/messages | grep CloudAgent\n'),bufsize=10000000)
    # Send commands to device
    stdin.flush()
    while not stdout.channel.exit_status_ready():
        time.sleep(1)
    output = stdout.channel.recv(10000000)
    output2 = output.decode('ISO-8859-1')
    rmLog(target)
    log = newLog(target)
    with log as logger:
        logger.write('\n\n'+output2+'\n')
    # Close connection and log success
    run.close()

def go():
    # Loop counter
    n = 1
    while True:
        for fmc in lookoutlist.fmclist:
            with open('lookout.log','a') as g:
                g.write('['+str(datetime.datetime.now())+'] (tasc) ')
                g.write('Running TaSc event number ' + str(n) + ' for host ' + str(fmc.hostname)+'\n')
            try:
                ssh(fmc)
                with open('lookout.log','a') as g:
                    g.write('['+str(datetime.datetime.now())+'] (tasc) ')
                    g.write('Data for TaSc event ' + str(n) + ', host '+str(fmc.hostname)+' written to log.\n')
                n += 1
            except Exception as e:
                with open('lookout.log','a') as g:
                    g.write('['+str(datetime.datetime.now())+'] (tasc) ')
                    g.write('TaSc encountered an error or an escape sequence was detected.'+'\n'+str(e))
                pass
            time.sleep(10)
if __name__ == '__main__':
    go()
