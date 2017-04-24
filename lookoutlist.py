from lookout import Fmc

#Reminder: Fmc class default order + values:
#hostname=None, ipaddr=None, username='', passwd='', status='ok'

FMCa = Fmc('FMCa', '10.0.0.1', 'admin', 'Sourcefire')

fmclist = [FMCa]