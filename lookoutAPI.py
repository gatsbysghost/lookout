from eve import Eve
from eve.auth import BasicAuth

class PwAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource,
                   method):
        return username == 'cisco' and password == '2BlackEyes!'

app = Eve()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,auth=PwAuth)