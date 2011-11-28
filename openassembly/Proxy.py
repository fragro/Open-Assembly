import urllib2,uuid,simplejson,thread,base64,random

class _Method(object):
    # from jsonrpclib
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, *args):
        return self.__send(self.__name, args)

class Proxy():
    def __init__(self, service_url, auth_user = None, auth_password = None):
        self.service_url = service_url
        self.auth_user = auth_user
        self.auth_password = auth_password
    def call(self, method, params=None, success=None, failure=None):
        if success != None or failure != None:
            thread.start_new_thread(self.__call,(method, params, success, failure))
        else:
            result = self.__call(method,params)
            ###We are using Proxy as a notification service,no Exceptions please
            if result['error'] != None:
                #raise Exception(result['result'])
                return None
            else:
                return result['result']
    def __call(self, method, params=None, success=None, failure=None):
        try:
            id = random.randint(1,10000)
            data = simplejson.dumps({'method':method, 'params':params, 'id': id})
            req = urllib2.Request(self.service_url)
            if self.auth_user != None and self.auth_password != None:
                authString = base64.encodestring('%s:%s' % (self.auth_user, self.auth_password))[:-1]
                req.add_header("Authorization", "Basic %s" % authString)
            req.add_header("Content-type", "application/json")
            f = urllib2.urlopen(req, data)
            response = f.read()
            data = simplejson.loads(response)
        except IOError, (strerror):
            data = dict(result=None,error=dict(message='Network error. ' + str(strerror),code=None,data=None), id=id)
        except ValueError, (strerror):
            data = dict(result=None,error=dict(message='JSON format error. ' + str(strerror),code=None,data=None), id=id)

        if data["error"] != None:
            if failure != None:
                failure(data['error'])
        else:
            if success != None:
                success(data['result'])
        return data
    def __getattr__(self, name):
        return _Method(self.call, name)

if __name__ == "__main__":
    def onResult(result):
        print 'success :-) : ' + str(result)
    def onError(error):
        print 'failure :-( : ' + error['message']
    service = Proxy('http://www.desfrenes.com/service/hello')
    ## threaded call with callbacks
    #service.call('hello',{'name':'John Doe'},onResult,onError)
    ## non-threaded call with returned result
    result = service.hello('John Doe')
    print result
    #while 1:pass
