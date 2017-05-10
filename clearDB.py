from pymongo import MongoClient

client = MongoClient()
db = client.fmcDB
db.authenticate('lookout','HashBangFP')
canaries = db.canaries
coalmine = db.coalmine

canaries.remove()
coalmine.remove()