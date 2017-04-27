# README
## Lookout (a Cloud URL DB Status Checker Service)
### Architecture
This project is written in Python3, and assumes the following dependencies:

- apache2 (for the rudimentary webserver to check status)
- mongodb (database, for REST API)
- paramiko (Python library, for SSH access)
- eve (Python library, for REST API)


The basic structure is as follows:
1. lookout.py and tasc.py run concurrently (each has a while True loop in its main function)
2. lookoutlist.py contains the data structures and config for the FMCs (the ‘canaries’ in this ‘coalmine’)
2. tasc.py starts an SSH session to each monitored FMC from lookoutlist.py, every 45 seconds, to check status.
3. lookout.py checks the most recent logfile for each FMC (~/lookoutLog/[FMCHostname].log, looking for OK and Fail indicators.
4. lookout.py also updates the web server according to the HTML specified in lookoutweb.py after every check it performs.
5. lookoutAPI also runs concurrently with lookout.py and tasc.py, and this is the ListenAndServe function for the REST API element of this application. It draws its configuration from settings.py.