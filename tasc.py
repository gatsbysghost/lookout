#!/usr/bin/env python3

import sys # for the big red 'terminate' button
import time # for waiting
import os, os.path #for creating the logging fsys
import datetime # for getting system time

import paramiko # ssh methods

from lookoutlist import fmclist

#
# GLOBAL VARIABLES
#
# Logging File Setup
# Create a log folder in the server user's ~ directory
logloc = os.path.expanduser('~')
if not os.path.exists(logloc+'/lookoutLog'):
    os.makedirs(logloc+'/lookoutLog')
os.chdir(logloc+'/lookoutLog/')
# Initialize list of commands to be run.

#
# PRIMARY FUNCTIONS
#

def newLog(target):
    logfilename = target.hostname+'.log'
    logger = open(logfilename,'a')
    return logger

def rmLog(target):
    logfilename = target.hostname+'.log'
    if os.path.isfile(logfilename):
        os.remove(logfilename)

# ssh() is adapted from the work of Kirk Byers
# see: https://pynet.twb-tech.com/blog/python/paramiko-ssh-part1.html
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
        run.connect(target.ipaddr, username=target.user, password=target.passwd, look_for_keys=False, allow_agent=False)
    except:
        print('\nSSH ERROR: Check credentials and target IP address, and verify that '
               'the target is configured to allow SSH access from this host.')
        sys.exit(0)
    stdin, stdout, stderr = run.exec_command(('\nsudo -i\n'+target.passwd+'\n'),bufsize=10000000)
    time.sleep(3)
    # sudo -i and input password
    stdin.write("\nsudo -i\n"+target.passwd+'\n')
    stdin.flush()
    time.sleep(1)
    # Send commands to device
    stdin.write('cat /var/log/messages | grep CloudAgent\n')
    stdin.flush()
    time.sleep(45)
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
    #
    # MAIN LOOP
    #
    while True:
        for fmc in fmclist:
            print('Running TaSc event number ' + str(n) + 'for host ' + str(fmc.hostname))
            try:
                ssh(fmc)
                print('Data for TaSc event ' + str(n) + ', host '+str(fmc.hostname)+
                      ' written to log.')
                n += 1
            except:
                print ('\nTaSc encountered an error or an escape sequence was detected.'
                       '\nShutting down as gracefully as possible, given the circumstances.')
                sys.exit(0)
    exit()