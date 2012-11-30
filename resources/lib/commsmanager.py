import xbmc
import utils
import json
import urllib2

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
    
    def __init__(self,address,port):
        self.address = address
        self.port = port
        
    def executeJSON(self,query,params):
        data = '{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }'
        clen = len(data)
        utils.log(data,xbmc.LOGDEBUG)
        req = urllib2.Request("http://" + self.address + ":" + str(self.port) + "/jsonrpc", data, {'Content-Type': 'application/json', 'Content-Length': clen})
        f = urllib2.urlopen(req)
        response = json.loads(f.read())
        f.close()

        if(response.has_key('result')):
            return response['result']
        else:
            return None
