#README
##Lookout (a Cloud URL DB Status Checker Service)
###Architecture
This project is written in Python3, and assumes the following dependencies:

-paramiko (Python library)

The basic structure is as follows:

lookout.py and tasc.py run concurrently (each has a while True loop in its main function)
tasc.py starts an SSH session to each monitored FMC from lookoutlist.py, every 45 seconds, to check status.
lookout.py checks the most recent logfile for each FMC (~/lookoutList/\[FMCHostname\].log, looking for OK and Fail indicators.
lookout.py also updates the web server according to the HTML specified in lookoutweb.py after every check it performs.