## in this section some basic definition is set as follows :

#Just for reporting puposes, define  service name, application name
ENVIRONMENT = 'My Web Environment'

# the log files in the same local machine running this script or in remote hosts  valuese to be either : (True | False )
# name if this option set false, the script will search the files in the directories provided in localhost set in LOG_DIRS dictionary
REMOTE = True

# Apache systems list, hostnames or IPs of apache servers of the enviroment that will SSH accessed to search for access log files
#example HOSTS = [ {hostname: 'host1', log_folders: ['folder_path1', 'folder_path2'] }, ]
HOSTS = [
	{ hostname: 'localhost',
	  log_folders: ['/var/SP/weloadm/logs/weblogic/IDMDomain/wls_oam1'
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
