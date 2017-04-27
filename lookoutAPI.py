from eve import Eve
from eve.auth import BasicAuth

#class PwAuth(BasicAuth):
#    def check_auth(self, username, password, allowed_roles, resource,
#                   method):
#        return username == 'admin' and password == 'cisco123'

app = Eve()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)