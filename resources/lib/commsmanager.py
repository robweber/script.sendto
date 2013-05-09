import xbmc
import utils
import json
import urllib2
import base64

class CommsManager:

    def executeJSON(query,params):
        return None

class LocalComms(CommsManager):

    def executeJSON(self,query,params):
        #execute the json request
        json_response = xbmc.executeJSONRPC('{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }')

        json_object = json.loads(json_response)

        #return nothing if there was an error
        if(json_object.has_key('result')):
            return json_object['result']
        else:
            return None

class RemoteComms(CommsManager):
    address = None
    port = 80
    user = None
    password = None
    
    def __init__(self,address,port,user,password):
        self.address = address
        self.port = port
        self.user = user
        self.password = password
        
    def executeJSON(self,query,params):
        result = None
        
        data = '{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }'
        clen = len(data)
        utils.log(data,xbmc.LOGDEBUG)
        hostdetails = "http://" + self.address + ":" + str(self.port) + "/jsonrpc"
        req = urllib2.Request(hostdetails, data, {'Content-Type': 'application/json', 'Content-Length': clen})
        if self.password != '':
            base64string = base64.encodestring('%s:%s' % (self.user, self.password))[:-1]
            authheader =  "Basic %s" % base64string
            req.add_header("Authorization", authheader)		
        try:
            f = urllib2.urlopen(req)
            response = json.loads(f.read())
            f.close()

            if(response.has_key('result')):
                result = response['result']
        except:
            pass

        return result;
