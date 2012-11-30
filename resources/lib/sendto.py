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
                #create a local host
                local_host = XbmcHost("Local","127.0.0.1","8080")
                
                #get the address of the host
                remote_host = self.host_manager.getHost(selected_xbmc)

                #check if the remote player is currently playing something
                remote_player = remote_host.isPlaying()

                if(remote_player >= 0 and utils.getSetting("override_destination") == 'true'):
                    #we need to stop the player before sending the new file
                     remote_host.executeJSON('Player.Stop','{"playerid":' + str(remote_player) + '}')
                     self.sendTo(local_host,remote_host)
                 
                elif(remote_player >= 0 and utils.getSetting("override_destination") == "false"):
                    #we can't stop the player, notify the user
                    xbmcgui.Dialog().ok("SendTo",remote_host.name + " is in use","Programs settings do not allow override")

                elif(remote_player == -2):
                    #catch for if the player is off
                    xbmcgui.Dialog().ok("SendTo",remote_host.name + " is not running","Please turn on XBMC before sending media")
                    
                else:
                    #not playing anything, send as normal
                    self.sendTo(local_host,remote_host)
                
    def sendTo(self,local_host,remote_host):
        
        #get the player/playlist id
        playerid = str(local_host.isPlaying())
           
        #get the percentage played and position
        player_props = local_host.executeJSON("Player.GetProperties",'{"playerid":' + playerid + ', "properties":["percentage","position","speed"]}')

        #check if the player is currently paused
        if(player_props['speed'] != 0):
            #pause the playing file
            self.localPlayer.pause()
        
        #get a list of all items in the playlist
        playlist = local_host.executeJSON("Playlist.GetItems",'{"playlistid":' + playerid + ',"properties":["file","title"]}')

        #add these files to the other playlist
        remote_host.executeJSON('Playlist.Clear','{"playlistid": ' + playerid + '}')
        for aFile in playlist['items']:
            remote_host.executeJSON('Playlist.Add','{"playlistid":' + playerid + ',"item": {"file": "' + aFile['file'] + '" } }')

        #play remote playlist
        remote_host.executeJSON("Player.Open",'{"item": { "playlistid": ' + playerid + ',"position":' + str(player_props['position']) + ' } }')

        #pause the player
        self.pausePlayback(remote_host)

        #seek to the correct spot
        remote_host.executeJSON("Player.Seek",'{"playerid":' + playerid + ', "value":' + str(player_props['percentage']) + '}')

        #stop the current player
        self.localPlayer.stop()
        local_host.executeJSON('Playlist.Clear','{"playlistid": ' + playerid + '}')

        #unpause playback, if necessary
        if(utils.getSetting("pause_destination") == "false"):
            self.pausePlayback(remote_host)

    def pausePlayback(self,host):
        result = host.executeJSON('Player.GetActivePlayers','{}')
        attempt = 0
        
        while(len(result) == 0 and attempt < 10):
            result = host.executeJSON('Player.GetActivePlayers','{}')
            attempt = attempt + 1
            time.sleep(2)

        utils.log(str(result[0]['playerid']))
        if(len(result) != 0):
            #if the result is found, then finally pause this player
            host.executeJSON('Player.PlayPause','{"playerid":' + str(result[0]['playerid']) + "}")
            
