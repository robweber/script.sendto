import xbmc
import xbmcgui
import json
import urllib2
import time
import utils as utils
from hostmanager import HostManager,XbmcHost

class SendTo:
    host_manager = None
    localPlayer = None
    
    def __init__(self):
        #get list of all the hosts
        self.host_manager = HostManager()
       
        self.localPlayer = xbmc.Player()
        
    def run(self):
        
        #check if there is even a file playing
        if(self.localPlayer.isPlaying()):
            #figure out what xbmc to send to
            selected_xbmc = xbmcgui.Dialog().select("Select instance",self.host_manager.listHosts())

            if(selected_xbmc != -1):
                #get the address of the host
                xbmc_host = self.host_manager.getHost(selected_xbmc)

                #check if the remote player is currently playing something
                remote_player = self.remoteJSON(xbmc_host,'Player.GetActivePlayers','{}')

                if(len(remote_player) > 0 and utils.getSetting("override_destination") == 'true'):
                    #we need to stop the player before sending the new file
                     self.remoteJSON(xbmc_host.address,'Player.Stop','{"playerid":' + str(remote_player[0]['playerid']) + '}')
                     self.sendTo(xbmc_host)
                 
                elif(len(remote_player) > 0 and utils.getSetting("override_destination") == "false"):
                    #we can't stop the player, notify the user
                    xbmcgui.Dialog().ok("SendTo",xbmc_host.name + " is in use","Programs settings do not allow override")
                
                else:
                    #not playing anything, send as normal
                    self.sendTo(xbmc_host)
                
    def sendTo(self,xbmc_host):
        
        #get the player/playlist id
        jsonResult = self.localJSON("Player.GetActivePlayers",'{}')
        playerid = str(jsonResult[0]['playerid'])
           
        #get the percentage played and position
        player_props = self.localJSON("Player.GetProperties",'{"playerid":' + playerid + ', "properties":["percentage","position","speed"]}')

        #check if the player is currently paused
        if(player_props['speed'] != 0):
            #pause the playing file
            self.localPlayer.pause()
        
        #get a list of all items in the playlist
        playlist = self.localJSON("Playlist.GetItems",'{"playlistid":' + playerid + ',"properties":["file"]}')

        #add these files to the other playlist
        self.remoteJSON(xbmc_host,'Playlist.Clear','{"playlistid": ' + playerid + '}')
        for aFile in playlist['items']:
            self.remoteJSON(xbmc_host,'Playlist.Add','{"playlistid":' + playerid + ',"item": {"file": "' + aFile['file'] + '" } }')

        #play remote playlist
        self.remoteJSON(xbmc_host,"Player.Open",'{"item": { "playlistid": ' + playerid + ',"position":' + str(player_props['position']) + ' } }')

        #pause the player
        self.pausePlayback(xbmc_host)

        #seek to the correct spot
        self.remoteJSON(xbmc_host,"Player.Seek",'{"playerid":' + playerid + ', "value":' + str(player_props['percentage']) + '}')

        #stop the current player
        self.localPlayer.Stop()
        self.localJSON('Playlist.Clear','{"playlistid": ' + playerid + '}')

        #unpause playback, if necessary
        if(utils.getSetting("pause_destination") == "false"):
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
        utils.log(data,xbmc.LOGDEBUG)
        req = urllib2.Request("http://" + xbmc_host.address + ":" + str(xbmc_host.port) + "/jsonrpc", data, {'Content-Type': 'application/json', 'Content-Length': clen})
        f = urllib2.urlopen(req)
        response = json.loads(f.read())
        f.close()

        if(response.has_key('result')):
            return response['result']
        else:
            return None
