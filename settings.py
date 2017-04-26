fmcschema = {
    'hostname': {
        'type': 'string'
    },
    'ipaddr': {
        'type': 'string'
    },
    'status': {
        'type': 'string'
    },
    'failcode': {
        'type': 'string'
    }
}

overallschema = {
    'name': {
        'type': 'string'
    },
    'status': {
        'type': 'string'
    }
}

canaries = {
    'item_title': 'canary',
    'resource_methods': ['GET'],
    'schema': fmcschema
}

coalmine = {
    'resource_methods': ['GET'],
    'schema': overallschema
}

DOMAIN = {'canaries': canaries,
          'coalmine': coalmine}

#MONGO_USERNAME = 'cisco'
#MONGO_PASSWORD = '2BlackEyes!'

#MONGO_DBNAME = 'lookout_api_db'