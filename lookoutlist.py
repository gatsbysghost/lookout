#author: Scott Reu (sreu@cisco.com)

from lookout import Fmc

#Reminder: Fmc class default order + values:
#hostname=None, ipaddr=None, username='', passwd='', status='ok'

FMCa = Fmc('gmccolluTestFMC', '14.36.117.118', 'admin', 'cisco')

fmclist = [FMCa]