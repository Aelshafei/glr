# glr | Generic Log Reporter
Python script to search   log files from one or more application servers based on required criteria


## Features
- Processing log files from several application servers of the same web environment using SSH or just one local server
- Send reports by Emails
- Eligible to fetch application logs based on custom LogLevel patterns
- No need to install custom Python modules
- Support legacy Python versions (Python 2.4)
- Easy Configuration


## How It Works
1- first, it loads the configuration from ```conf.py``` to define the following :
- The period needed to get report about (1 day, 2h ..etc )
- From where the log files will be got (Remotely or locally)

2- get the files from its location to a temp folder

3- loading the log lines and fetching Data based on the LogLevel configuration

4- generating and formating report data

5- delete log files from the temp directory

    

## How to use

1. set project configuration in ```conf.py``` file
```
## in this section some basic definition is set as follows :

#Just for reporting puposes, define  service name, application name
ENVIRONMENT = 'My Web Environment'

# the log files in the same local machine running this script or in remote hosts  valuese to be either : (True | False )
# name if this option set false, the script will search the files in the directories provided in localhost set in LOG_DIRS dictionary
REMOTE = True

#  systems list, hostnames or IPs of apache servers of the enviroment that will SSH accessed to search for access log files
#example HOSTS = [ {hostname: 'host1', log_folders: ['folder_path1', 'folder_path2'] }, ]
HOSTS = [
	{ hostname: 'localhost',
	  log_folders: ['/log/path'
	  				],
	},
	]

#System username for remote hosts
USERNAME='weloadm'



# Log levels to search for
LOG_LEVELS = ['ERROR']

# Tempraroy directory, where the log files will be copied into and extracted temporary for manipulation before deleting them
TEMP_DIR = '/home/aelshafei/a2lr_tmp'


# Default period of Reporting in hours (h) or minutes (m) or days(d), Format: 1d or 2h or 30m 
PERIOD= '200d'

#Is it needed to send an email when running the script
SEND_EMAIL = True

#list of emails to receive an email report .. example : TO_EMAILS = ['elshafei.ah@gmail.com', 'a@b.c', 'd@e.f']

TO_EMAILS = ['elshafei.ah@gmail.com']


```


2- in case of ```REMOTE``` mode, make sure that remote servers can be automatically SSH connected using keys without prompting password

3- in case of sending report to emails, configure a local SMTP server, add the receptions to ```TO_EMAILS``` in ```conf.py``` file

5- run ```glr.py``` manually or using crontab and enjoy :-)
