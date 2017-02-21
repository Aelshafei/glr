#!/usr/bin/python

#######################################################################
#
# Analysing allication log files to get needed logs from 
#
# Author: Ahmed ElShafei [elshafei.ah@gmail.com]
#
# NOTE: consider changing the constants in the conf.py file
#
# Description:
# This is a Python script to search error logs in application log files from one or more application servers
#
# Change log:
# 08.02.2017	Ahmed ElShafei	Script created
#
#######################################################################


#Let's Play

##################################################
# Section 00. Importing Python Libraries 		 #
##################################################

import sys
import os
import time
import shutil
import re
import datetime
import collections
import operator
import pprint
import csv
import math
import commands
import smtplib
import getpass
import socket
import subprocess

##################################################
# Section 01. DEFINIONS 				   	     #
##################################################

# for modularity, configuration is set in seprate file and other helper classes as well, We're going to import it as  modules
from conf import *
from ssh import *
from helpers import *


# computing reference time to discard log lines older than that time based on PERIOD value
START_DATE = datetime.datetime.now()
period_args = ''.join(conf.PERIOD.split())
period_measure = period_args[-1].lower()
period_val = period_args[0:-1]
if not period_measure in ('h', 'd', 'm'):
	print('\t' + bcolors.FAIL + 'Not valid PERIOD measure unit, please use either m for minutes, h for hours or d for days' + bcolors.ENDC)
	exit(1)
#check if period value is valid
try:
	period_val = int(period_val)
	if period_val < 1 :
		print('\t' + bcolors.FAIL + 'Not valid PERIOD value, please set positive number value ' + bcolors.ENDC)
		exit(1)
except Exception:
	print('\t' + bcolors.FAIL + 'Not valid PERIOD value, please set value in numbers' + bcolors.ENDC)
	exit(1)

if period_measure == 'h':
	dt_ref = START_DATE - datetime.timedelta(hours=period_val)
elif period_measure == 'm':
	dt_ref = START_DATE - datetime.timedelta(minutes=period_val)
else:
	dt_ref = START_DATE - datetime.timedelta(days=period_val)

#print dt_ref


##################################################
# Section 02. INTIALIZATION 				     #
##################################################


print(' * Intializing ....\n')



# Check if the Tempraroy directory exist, otherwise create it
print(' * checking temporary directory ....')
if not os.path.exists(TEMP_DIR):
	print('\t Tempraroy directory not found, creating into ' + TEMP_DIR)
	os.makedirs(TEMP_DIR)
	print('\t .. ' + bcolors.OKGREEN + 'DONE' + bcolors.ENDC + '\n')
else:
	print('\t Tempraroy directory at ' + TEMP_DIR + ' already exists\n')


# Check if the data directory exist, otherwise create it
print(' * checking data directory ....')
if not os.path.exists('DATA'):
	print('\t Data directory not found, creating .. '  )
	os.makedirs('DATA')
	print('\t .. ' + bcolors.OKGREEN + 'DONE' + bcolors.ENDC + '\n')
else:
	print('\t Data directory at ' + 'DATA' + ' already exists\n')



# check whether log files to be remotely searched or locally
print(' * check whether log files to be remotely searched or locally')
if REMOTE:
	print('\t Files to be searched remotely\n')
	#check if Hosts is SSH accessable
	sshSessions = []	# a list of SSH sessions to be intitiated
	print(' * check if Hosts is accessable normally !')
	for host in HOSTS:
		sshSession = SSH(host['hostname'], '', USERNAME, 22)
		sshSessions.append( sshSession )
		result = sshSession.cmd('echo Ok')
		if 'Ok' in result:
			print('\t ' + host['hostname'] + ' can be accessed successfully')
		else:
			print('\t' + 'Error accessing ' + host['hostname'] )
			exit(1)
	print('\n')
else:
	print('\t Files to be searched locally\n')


# getting log files into the temporary directory
if REMOTE:
	print(' * getting log files from remote servers')
	for sshSession in sshSessions:
		#getting the list of files to be copied from the remote log directory
		#generating the placeholder of time frame in oder to be append in find command
                host = (item for item in HOSTS if item["hostname"] == sshSession.ip).next()
		for host_log_dir in host['log_folders']:
			period_placeholder = calculate_period()
			print("log dir : " + host_log_dir ) 
			logfiles = sshSession.cmd('find '  +  host_log_dir.replace(" ", "") + ' -type f '   + period_placeholder )
		        print('find '  + '-type f ' + host_log_dir.replace(" ", "") + period_placeholder )
			logfiles_list = []
  			for string in logfiles.split():
                        	if host_log_dir in string:
					if '*' not in string:
						logfiles_list.append(string)
			print(logfiles_list)
			print('\t' + str(len(logfiles_list)) + ' log files found in ' + sshSession.ip + '\n')
			if len(logfiles_list):
				for logfile in logfiles_list:
					scp_output = sshSession.pull(logfile, TEMP_DIR + '/' + sshSession.ip + logfile.replace('/', '_') )
					if '100%' in scp_output:
						print('\t' + logfile + ' successfully copied from ' + sshSession.ip + ' to ' + TEMP_DIR + '\n')
					else:
						print('\t Error coping' + logfile + ' from ' + sshSession.ip + '\n')
						exit(1)

	print('\t ... DONE')
	print('\n')

else:
	print(' * getting files from local server')
	#calculating second based on PERIOD configuration
	local_index = next(index for (index, d) in HOSTS if d["hostname"] == 'localhost')
	period_placeholder = calculate_period()
	past = time.time() - period_placeholder
	logfiles = []
	for directory in HOSTS[local_index]['log_folders']:
		for p, ds, fs in os.walk(directory):
		    for fn in fs:
		        filepath = os.path.join(p, fn)
		        if os.path.getmtime(filepath) >= past and COMMON_LOGFILE_NAME in filepath :
		            logfiles.append(filepath)


	print ('\t ' + str(len(logfiles)) + ' files found in the local directories ')

	for logfile in logfiles:
		shutil.copy2(logfile, TEMP_DIR + '/' + 'localhost' + logfile.replace('/', '_') )
		print ('\t' + logfile + ' copied to ' + TEMP_DIR)
	print('\n')



##################################################
# Section 03. Reading logfiles 				     #
##################################################



logs = [] #this list will hold the log lines


print(' * reading log files ..')
#loading log line from log giles
for log_file in os.listdir(TEMP_DIR):
	#print log_file
	log_file_path = os.path.join(TEMP_DIR, log_file)
	if os.path.isfile(log_file_path):
		host_file_logs = []
		logs.append({'log_host': log_file_path.split('_')[0].split('/')[-1], 'log_file': '/' + '/'.join(log_file_path.split('_')[1:]), 'host_file_logs': host_file_logs })
		for line in open(log_file_path, 'r').readlines():
			#print line
			log_type = contains_loglevel(line)
			if len(line) > 0 and line[0] != '#' and log_type:
				line_log = line.split(']', 1)[1]
				index = any_dicts_have_value(host_file_logs, 'log_line', line_log)
				if index:
					host_file_logs[index - 1].update({'count': host_file_logs[index - 1]['count'] + 1})
				else:
					#line_details['time_stamp'] = time.strptime(line_details['time_stamp'][1:-1].split('_')[0], '%d/%b/%Y:%H:%M:%S')
					line_details = {}
					line_details.update({'log_line' : line_log})
					line_details.update({'count': 1})
					#filter odd log line. ex: 84.3.41.146 - - [03/Feb/2016:12:00:14 +0100] "-" 408 - "-" "-" 7
					log_timestamp_string = line.split(']', 1)[0][1:].split('.')[0]
					log_timestamp = time.strptime(log_timestamp_string, '%Y-%m-%dT%H:%M:%S')
					if  datetime.datetime(*log_timestamp[0:6]) > dt_ref:
						line_details.update({'log_type': LOG_LEVELS[log_type -1]})
						host_file_logs.append(line_details)

#pprint.pprint( logs[0] )

#print( len(logs) )

print ('\t ' + str(len(logs)) + ' log lines loaded ..\n')





##################################################
# Section 04. Processing logs 				     #
##################################################

__NO_LOGS = 0
log_hosts = []
log_files = []
print(logs)
for log in logs: 
	for host_file_log in log['host_file_logs']:
		__NO_LOGS += host_file_log['count']
  		if log['log_host'] not in log_hosts:
			log_hosts.append(log['log_host'])
       		if log['log_file'] not in log_files:
			log_files.append(log['log_file'])

__NO_FILES = len(log_files)
__NO_HOSTS = len(log_hosts)
print('lgo files no: ' + str(__NO_FILES))
# No need for further processing - this section was only required for a2lr https://github.com/Aelshafei/a2lr :)


print('\t Peocessing done, formatting for printing ..\n\n')
##################################################
# Section 05. Report formatting 				 #
##################################################

#
#test
#

if SEND_EMAIL:
	__LOG_DATA = '' 
	

	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__ENVIRONMENT', ENVIRONMENT)
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__PERIOD_FRAME', PERIOD )
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__START_DATE', START_DATE.strftime("%Y-%m-%d %H:%M:%S"))
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__FROM_EMAIL', getpass.getuser() + '@' +  socket.gethostname())
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__TO_EMAILS', ', '.join(TO_EMAILS) )
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__SUBJECT', ENVIRONMENT + ' | glr ')
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__NO_FILES', str(__NO_FILES) )
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__NO_HOSTS', str(__NO_HOSTS) )
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__NO_LOGS', str(__NO_LOGS) )
	EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__LOG_LEVELS', ', '.join(LOG_LEVELS)  )
	SHELL_CMD_TEMPLATE = SHELL_CMD_TEMPLATE.replace('__TO_EMAILS', ', '.join(TO_EMAILS) )
        SHELL_CMD_TEMPLATE = SHELL_CMD_TEMPLATE.replace('__SUBJECT', ENVIRONMENT + ' | glr ')



#printing http status
print(bcolors.HEADER + 'Logs found :' + bcolors.ENDC)
for log in logs:
	print('* Printing logs in file: ' + log['log_file'] + ' at host: ' + log['log_host'])
	for host_file_log in log['host_file_logs']:
		print( '   ' + str(host_file_log['count']) + host_file_log['log_line'] )
		if SEND_EMAIL:
			__LOG_DATA  += ('<tr>\n'
											  '<td style="background-color: #A1C6DF; color: black;min-width:50px;padding:5px">\n'
											   + host_file_log['log_type'] + 
											   ' </td>\n'
											   '<td style="background-color: #A1C6DF; color: black;min-width:50px;padding:5px">\n'
											   +  log['log_host'] + 
											   ' </td>\n'
											   '<td style="background-color: #A1C6DF; color: black;min-width:50px;padding:5px">\n'
											   +  log['log_file'] + 
											   ' </td>\n'
											   '<td style="background-color: #A1C6DF; color: black;min-width:50px;padding:5px">\n'
											   + str(host_file_log['count']) + 
											   ' </td>\n'
											   '<td style="background-color: #A1C6DF; color: black;min-width:50px;padding:5px">\n'
											   +  host_file_log['log_line'] + 
											   ' </td>\n'
											)


print('\n')

if SEND_EMAIL:
        EMAIL_HTML_TEMPLATE =  EMAIL_HTML_TEMPLATE.replace('__LOG_DATA', __LOG_DATA)
        f = open('DATA/email.html', 'w')
        f.write(EMAIL_HTML_TEMPLATE)
        f.close()
        f = open('sendmail.sh', 'w')
        f.write(SHELL_CMD_TEMPLATE)
        f.close()
        print('\n\n * Sending email report ..')
        print('\n\n * Sending email report ..')
        try:
                #smtpObj = smtplib.SMTP('localhost')
                #smtpObj.sendmail( 'test@test.com', TO_EMAILS , EMAIL_HTML_TEMPLATE)
                subprocess.call(["./sendmail.sh"])
                #process = subprocess.Popen('mail', '-s', '$(echo -e "[VFDE] PROD -- CC Report\nContent-Type: text/html")' , '-c', TO_EMAILS, EMAIL_HTML_TEMPLATE)
                print " \t Successfully sent email .."
        except Exception , e:
                print str(e)


##################################################
# Section 02. Finazlization 				     #
##################################################

#remove temp log files
for file in os.listdir(TEMP_DIR):
    file_path = os.path.join(TEMP_DIR, file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception , e:
        print(e)



