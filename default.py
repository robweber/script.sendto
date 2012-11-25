import xbmc
import json
import urllib2
import resources.lib.utils as utils

class Neighborhood:

    def run(self):
        utils.log("Running addon")

        #get the currently playing file
        player = self.getJSON("Player.GetActivePlayers",'{}')
        
        current_player = player[0]['playerid']
        utils.log("Current Player: " + player[0]['type'])

        #get the properties
        player_props = self.getJSON("Player.GetProperties",'{"playerid":' + str(current_player) + ', "properties":["percentage"]}')
        utils.log(str(player_props['percentage']))
        
        #get the currently playing file
        playing_file = self.getJSON("Player.GetItem",'{"playerid":' + str(current_player) + ',"properties":["file"]}')
        utils.log(playing_file['item']['file'])

        #send this to the other instance
        self.sendJSON("Player.Open",'{"item": {"file":"' + playing_file['item']['file'] + '"},"options":{"resume":' + str(player_props['percentage']) + '}}')

        #stop the current player
        #self.getJSON('Player.Stop','{"playerid":' + str(current_player) + '}')

    def getJSON(self,query,params):
        #execute the json request
        json_response = xbmc.executeJSONRPC('{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }')

        json_object = json.loads(json_response)

        #return nothing if there was an error
        if(json_object.has_key('result')):
            return json_object['result']
        else:
            return None

    def sendJSON(self,query,params):
        utils.log("sending video")
        data = '{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }'
        utils.log(data)
        clen = len(data)
        req = urllib2.Request("http://192.168.1.112/jsonrpc", data, {'Content-Type': 'application/json', 'Content-Length': clen})
        f = urllib2.urlopen(req)
        response = f.read()
        utils.log(response)
        f.close()


Neighborhood().run()
