#author: Scott Reu (sreu@cisco.com)

import os
import lookoutlist
import lookout

def updateHTML():
	html = ''

	html += '<!doctype html>'
	html += '<html lang="en">'
	html += '<head>'
	html += '<meta charset="utf-8">'
	html += '<title style="text-align:center;">Firepower Cloud URL DB Status Checker</title>'
	html += '<meta name="description" content="Lookout: a Brightcloud/TALOS Monitoring Server">'
	html += '<meta name="author" content="Scott Reu (sreu) & Garrett McCollum (gmccollu)">'
	html += '<link rel="stylesheet" href="css/styles.css?v=1.0">'
	html += '</head>'
	html += '<body>'
	html += '<style>'
	html += 'table {border-collapse:collapse;}'
	html += 'td, th {border:1px solid black; text-align:left; padding:3px;}'
	html += '</style>'
	html += '<p><span style="font-size:xx-large; font-weight:bold; align:center;">Brightcloud URL DB Status</span></p>'
	html += '<table>'
	html += '<tbody>'
	html += '<br>'
# Top Row (Header)
	html += '<tr>'
	html += '<td><b>FMC Hostname</b></td>'
	html += '<td><b>IP Address</b></td>'
	html += '<td><b>Status</b></td>'
	html += '<td><a href ="https://techzone.cisco.com/t5/Security-Intelligence-DNS/How-to-interpret-Cloud-Agent-URL-Filtering-Download-Failure/ta-p/589210">'
	html += '<b>Failure Code</b></a></td>'
	html += '</tr>'
# Add statuses for each FMC; color-code
	for fmc in lookoutlist.fmclist:
		html += '<tr style="background-color:'

		if fmc.status == 'ok':
			html += 'lime'
		else:
			html += 'red'

		html += ';">'

		html += '<td>'+fmc.hostname+'</td>'
		html += '<td>'+fmc.ipaddr+'</td>'
		html += '<td>'+fmc.status+'</td>'
		if fmc.status == 'fail':
			html += '<td>'+fmc.failcode+'</td>'
		else:
			html += '<td>n/a</td>'
	html += '</tr>'
	html += '</tbody>'
	html += '</table>'
# Overall Status Table
	html += '<table>'
	html += '<tbody>'
	html += '<tr>'
	html += '<td><b>Overall Status of Cloud Services</b></td>'
	html += '</tr>'
	if lookout.cloudStatus() == 'fail':
			html += '<tr style="background-color:red;"><td>Overall Status: Failed'
	elif lookout.cloudStatus() == 'ok':
			html += '<tr style="background-color:lime;"><td>Overall Status: OK'
	html += '</td></tr>'
	html += '</tbody>'
	html += '</table>'
	html += '</body>'
	html += '</html>'
	with open('/var/www/html/index.html','w') as f:
		f.write(html)