import os
import lookoutlist

os.chdir('/var/www/html')

def updateHTML():
	html = ''

	html += '<!doctype html>'
	html += '<html lang="en">'
	html += '<head>'
	html += '<meta charset="utf-8">'
	html += '<title>Firepower Cloud URL DB Status</title>'
	html += '<meta name="description" content="Lookout: a Brightcloud/TALOS Monitoring Server">'
	html += '<meta name="author" content="Scott Reu (sreu) & Garrett McCollum (gmccollu)">'
	html += '<link rel="stylesheet" href="css/styles.css?v=1.0">'
	html += '</head>'
	html += '<body>'
	html += '<table>'
	html += '<tbody>'
# Top Row (Header)
	html += '<th>'
	html += '<tr>'
	html += '<td>FMC Hostname</td>'
	html += '<td>IP Address</td>'
	html += '<td>Status</td>'
	html += '<td>Failure Code</td>'
	html += '</tr></th>'
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
			html += '<td>'+fmc.code+'</td>'
		else:
			html += '<td>n/a</td>'
	html += '</tr>'
	html += '</tbody>'
	html += '</table>'
# Overall Status Table
	html += '<table>'
	html += '<tbody>'
	html += '<th>'
	html += '<tr>'
	html += '<td>Overall Status of Cloud Services</td>'
	html += '</tr></th>'
	okCount = 0
	failCount = 0
	for fmc in lookoutlist.fmclist:
		if fmc.status == 'ok':
			okCount += 1
		elif fmc.status == 'fail':
			failCount += 1

	if (okCount + failCount) == 1:
		if failCount == 1:
			html += '<tr style="background-color:red;"><td>Overall Status: Failed'
		else:
			html += '<tr style="background-color:lime;"><td>Overall Status: OK'
	elif okCount + failCount > 1:
		if failCount >= 2:
			html += '<tr style="background-color:red;"><td>Overall Status: Failed'
		else:
			'<tr style="background-color:lime;"><td>Overall Status: OK'
	html += '</td></tr>'
	html += '</tbody>'
	html += '</table>'
	html += '</body>'
	html += '</html>'
	with open('index.html','w') as f:
		f.write(html)