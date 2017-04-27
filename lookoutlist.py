#author: Scott Reu (sreu@cisco.com)

from lookout import Fmc

#Reminder: Fmc class default order + values:
#hostname=None, ipaddr=None, username='', passwd='', status='ok'

rtpFMC = Fmc('Lookout_RTP_FMC', '172.18.124.211', 'admin', 'S0urceF!reRTP')

fmclist = [rtpFMC]
