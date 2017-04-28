# README
## Lookout (a Cloud URL DB Status Checker Service)
### Server Administration
- **NOTE: Any time the server reboots, it will be necessary to manually start the mongodb engine.** The command to do so is:
`sudo mongod --fork --config /etc/mongod.conf --auth`
- Three main services auto-start with systemd (config files in /lib/systemd/system):
	- tasc (Automated SSH to monitored FMCs)
	- lookout (Status Checker & Database Updater)
	- lookoutAPI (ListenAndServe application for REST API access)
- systemctl can be used to manage these services (start, stop, status, enable, disable)
- Logging for tasc and lookout is sent to the unified logfile /home/support/lookoutList/lookout.log
	- This logfile is automatically deleted every Monday at 3:30am system time (i.e., we keep logs for at most a week—this was scheduled with crontab and can be modified there if necessary)
### Source files (in /home/support/code/lookout)
- **tasc.py**: a loop that runs while True, collecting updates from each FMC we choose to monitor.
- **lookout.py**: a loop that runs while True, grepping the logs collected by tasc.py and checking to see whether more than one of the FMCs we’re monitoring has failed to get updates from brightcloud. This also contains the definition of the **Fmc** class, which is used throughout the program.
- **lookoutlist.py**: the list of FMCs which we’re choosing to monitor.
- **lookoutweb.py**: a script to update the http daemon on the server with a friendly (if sparse) readout of each FMC’s status and the overall global status. This is for diagnostic purposes only, and will be deprecated in future versions.
- **lookoutAPI.py**: This runs while true to ListenAndServe our REST API on a given port.
- **settings.py**: Settings for the lookoutAPI.

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
### REST API Interface
The REST API for Lookout is configured to return data (read-only) from two collections when it receives GET requests: **canaries** and the **coalmine**. **Canaries** are individual FMCs, and a canary (\<LookoutServerURL\>/canaries/\<FMC\_hostname\>) returns JSON like this (where objectID is a UUID):

	{
	 “_created": "Thu, 01 Jan 1970 00:00:00 GMT",
	 "hostname": "TestFMC",
	 "failcode": "",
	 "ipaddr": “1.1.1.1”,
	 “_updated": "Thu, 01 Jan 1970 00:00:00 GMT",
	 “_etag": “<eTag>”,
	 "status": "ok",
	 “_links": \{
		"parent": \{
		  "title": "home",
		  "href": "/"
		},
		"collection": {
		  "title": "canaries",
		  "href": "canaries"
		},
		"self": {
		  "title": "canary",
		  "href": "canaries/<objectID>"
		}
	 },
	 “_id": "<objectID>"
	}

The **coalmine** is the global status (i.e., the computed status of the URL Filtering cloud, taking into account individual unit failures). The JSON of \<LookoutServerURL\>/coalmine/global looks like this:

	{
	 “_created": "Thu, 01 Jan 1970 00:00:00 GMT",
	 “_id": "<objectID>",
	 “_links": {
		"parent": {
		  "title": "home",
		  "href": "/"
		},
		"collection": {
		  "title": "coalmine",
		  "href": "coalmine"
		},
		"self": {
		  "title": "Coalmine",
		  "href": "coalmine/<objectID>"
		}
	 },
	 “_etag": "<eTag>",
	 "status": "ok",
	 "name": "global",
	 “_updated": "Thu, 01 Jan 1970 00:00:00 GMT"
	}

