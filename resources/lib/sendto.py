import xbmc
import xbmcgui
import json
import urllib2
import time
import utils as utils
from hostmanager import HostManager,XbmcHost

class SendTo:
    host_manager = None
    
    def __init__(self):
        #get list of all the hosts
        self.host_manager = HostManager()
        
    def run(self):
        #figure out what xbmc to send to
        selected_xbmc = xbmcgui.Dialog().select("Select instance",self.host_manager.listHosts())

        if(selected_xbmc != -1):
            #get the address of the host
            xbmc_host = self.host_manager.getHost(selected_xbmc)

            if(utils.getSetting("override_destination") == 'false'):
                #check if the backend is currently playing something
                playing_backend = self.remoteJSON(xbmc_host,'Player.GetActivePlayers','{}')

                if(len(playing_backend) != 0):
                    xbmcgui.Dialog().ok("SendTo",xbmc_host.name + " is in use","Programs settings do not allow override")
                else:
                    self.sendTo(xbmc_host)
            else:
                self.sendTo(xbmc_host)

    #get the active player
    #pause the active player
    #get the percentage played and position of the current item (Player.GetProperties)
    #get a list of all the items (Playlist.GetItems)
    #clear the remote playlist (if playing)
    #add this list to the remote playlist (Playlist.Add)
    #play the remote playlist (Player.Open)
    #seek to the position required (Player.Seek)
    #stop the local player (Player.Stop)
    #clear the playlist (Playlist.Clear)
                
    def sendTo(self,xbmc_host):
        #get the local playing file
        player = self.localJSON("Player.GetActivePlayers",'{}')
        current_player = str(player[0]['playerid'])
           
        #get the percentage played
        player_props = self.localJSON("Player.GetProperties",'{"playerid":' + current_player + ', "properties":["percentage"]}')
            
        #get the currently playing file
        playing_file = self.localJSON("Player.GetItem",'{"playerid":' + current_player + ',"properties":["file"]}')
        utils.log("Sending " + playing_file['item']['file'] + " to " + xbmc_host.name)

        #send this to the other instance
        self.remoteJSON(xbmc_host,"Player.Open",'{"item": {"file":"' + playing_file['item']['file'] + '"},"options":{"resume":' + str(player_props['percentage']) + '}}')

        #stop the current player
        self.localJSON('Player.Stop','{"playerid":' + current_player + '}')
       
        if(utils.getSetting("pause_destination") == "true"):
            self.pausePlayback(xbmc_host)

    def pausePlayback(self,host):
        result = self.remoteJSON(host,'Player.GetActivePlayers','{}')
        attempt = 0
        
        while(len(result) == 0 and attempt < 10):
            result = self.remoteJSON(host,'Player.GetActivePlayers','{}')
            attempt = attempt + 1
            time.sleep(2)

        utils.log(str(result[0]['playerid']))
        if(len(result) != 0):
            #if the result is found, then finally pause this player
            self.remoteJSON(host,'Player.PlayPause','{"playerid":' + str(result[0]['playerid']) + "}")
            
    
    def localJSON(self,query,params):
        #execute the json request
        json_response = xbmc.executeJSONRPC('{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }')

        json_object = json.loads(json_response)

        #return nothing if there was an error
        if(json_object.has_key('result')):
            return json_object['result']
        else:
            return None

    def remoteJSON(self,xbmc_host,query,params):
        data = '{ "jsonrpc" : "2.0" , "method" : "' + query + '" , "params" : ' + params + ' , "id":1 }'
        clen = len(data)
        
        req = urllib2.Request("http://" + xbmc_host.address + ":" + str(xbmc_host.port) + "/jsonrpc", data, {'Content-Type': 'application/json', 'Content-Length': clen})
        f = urllib2.urlopen(req)
        response = json.loads(f.read())
        f.close()

        if(response.has_key('result')):
            return response['result']
        else:
            return None
