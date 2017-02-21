import conf

#Command line escape sequences for output formating
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def any_dicts_have_value(iterable, key, value):
    for element in iterable:
        if value == element[key]:
            return iterable.index(element) + 1
    return False

def contains_loglevel(log):
	for log_level in conf.LOG_LEVELS:
		if log_level in log:
			return conf.LOG_LEVELS.index(log_level) + 1
	return False



#function to generate the period placeholder for log files searching command
def calculate_period():
	#based on PERIOD constant definition, local and remote command placeholders to be calculated

	#removing any whitespaces and fetching PERIOD args
	period_args = ''.join(conf.PERIOD.split())
	period_measure = period_args[-1].lower()
	period_val = period_args[0:-1]

	#print period_measure
	#check if period measure unit is valid
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


	if period_measure == 'm':
		if conf.REMOTE:
			period_placeholder = '-mmin -' + str(period_val)
		else:
			period_placeholder = 60 * period_val
	elif period_measure == 'h': 
		if conf.REMOTE:
			period_placeholder = '-mmin -' + str(period_val * 60)
		else:
			period_placeholder = 60 * 60 * period_val
	else: 
		#days
		if conf.REMOTE:
			period_placeholder = '-mtime -' + str(period_val)
		else:
			period_placeholder = 60 * 60 * 24 * period_val

	

	#print period_placeholder
	return period_placeholder


SHELL_CMD_TEMPLATE = '''#!/bin/bash

 mailx -v -s "$(echo -e "__SUBJECT \nContent-Type: text/html")"  __TO_EMAILS  < DATA/email.html

'''

EMAIL_HTML_TEMPLATE = '''


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>

	<body style="margin-top: 0; margin-right: 0; margin-bottom: 0; margin-left: 0;padding-top: 0; padding-right: 0; padding-bottom: 0; padding-left: 0;min-width: 400px">
		<table style="font-family: 'trebuchet MS';" width="100%" border="0" cellspacing="0" cellpadding="0">
			<tr>
				<td align="center">
					<h2 style="color:#CD2A25;text-align"> __ENVIRONMENT | Generic log Reporter (glr) </h2>
				</td>
			</tr>
		</table>
		<table style="width:100%; font-family: 'trebuchet MS';" >
			<tr>
				<td style="text-align:left;display:inline;width:33%" ><h3 style="font-weight: normal;display:inline"><b>Period Frame : </b> __PERIOD_FRAME </h3></td>
			</tr>
			<tr>	
				<td style="text-align:left;display:inline;width:33%"><h3 style="font-weight: normal;display:inline"><b>Start Date : </b> __START_DATE </h3></td>
			</tr>
			 <tr>
                                <td style="text-align:left;display:inline;width:33%"><h3 style="font-weight: normal;display:inline"><b>Log Levels : </b> __LOG_LEVELS </h3></td>
                        </tr>
			<tr>
				<td align="center"> <span stlye="text-align"><b style="color:#CD2A25">__NO_LOGS</b>  logs found in <b style="color:#CD2A25">__NO_FILES</b> files at <b style="color:#CD2A25">__NO_HOSTS</b> hosts</span></td>
			</tr>
		</table>

		
		<div style="clear:both"></div>
		<br/>
		
		<table style="width:100%; font-family: 'trebuchet MS';">
			<tr>
			<td style="text-align:left;display:inline; float:left" >
				<table cellpadding="3" cellspacing="2" style="border: thin solid #FFFFFF; font-size: 16px; font-family: 'trebuchet MS';">
					<tr>
						<td style="background-color: #1D5E89; color: white; font-weight: bold;max-width:40px;padding:5px">
							  Log Type</td>
						<td style="background-color: #1D5E89; color: white; font-weight: bold;max-width:40px;padding:5px">
							  Log Host</td>
						<td style="background-color: #1D5E89; color: white; font-weight: bold;max-width:40px;padding:5px">
							  Log Dir</td>
						<td style="background-color: #1D5E89; color: white; font-weight: bold;max-width:40px;padding:5px">
							  Log Count</td>
						<td style="background-color: #1D5E89; color: white; font-weight: bold;min-width:100px;padding:5px">
							  Log Details</td>
						
					</tr>
					__LOG_DATA
					  
				</table>
			</td>
		</table>
		<div style="clear:both"></div>
		<br/>
		
		
	</body>
</html>

'''

