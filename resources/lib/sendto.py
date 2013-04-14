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
            selected_xbmc = xbmcgui.Dialog().select(utils.getString(30036),self.host_manager.listHosts())

            if(selected_xbmc != -1):
                #create a local host
                local_host = XbmcHost("Local","127.0.0.1",utils.getSetting("local_host_port"),utils.getSetting("local_host_user"),utils.getSetting("local_host_password"))
                
                #get the address of the host
                remote_host = self.host_manager.getHost(selected_xbmc)

                #check if the remote player is currently playing something
                remote_player = remote_host.isPlaying()

                if(remote_player >= 0 and utils.getSetting("override_destination") == 'true'):
                     #we need to stop the player before sending the new file
                     remote_host.stop()
                     self.sendTo(local_host,remote_host)
                 
                elif(remote_player >= 0 and utils.getSetting("override_destination") == "false"):
                    #we can't stop the player, notify the user
                    xbmcgui.Dialog().ok("SendTo",remote_host.name + " " + utils.getString(30039),utils.getString(30037))

                elif(remote_player == -2):
                    #catch for if the player is off
                    xbmcgui.Dialog().ok("SendTo",remote_host.name + " " + utils.getString(30040),utils.getString(30038))
                    
                else:
                    #not playing anything, send as normal
                    self.sendTo(local_host,remote_host)

    def reverse(self,remote_host):
        #do a regular "sendto" but reverse the local and remote hosts
        local_host = XbmcHost("Local","127.0.0.1","8080","","")

        self.sendTo(remote_host,local_host,True)
    
    def sendTo(self,local_host,remote_host,reverse=False):
        
        #get the player/playlist id
        playerid = str(local_host.isPlaying())
           
        #get the percentage played and position
        player_props = local_host.playingProperties(playerid)

        #check if the player is currently paused
        if(player_props['speed'] != 0):
            #pause the playing file
            self.pausePlayback(local_host)

        #if reverse these checks don't matter
        keep_playing = True
        if(not reverse):
            #check if we should prompt to keep playback paused
            if(utils.getSetting("pause_prompt") == "true"):
                keep_playing = not xbmcgui.Dialog().yesno(utils.getString(30000),utils.getString(30041))
        
        #get a list of all items in the playlist
        playlist = local_host.getPlaylist(playerid)

        #add these files to the other playlist
        remote_host.addItems(playlist,playerid)

        #play remote playlist
        remote_host.playPosition(str(player_props['position']),playerid)

        #pause the player
        self.pausePlayback(remote_host)

        #seek to the correct spot
        remote_host.seekFile(player_props['percentage'],playerid)

        #stop the current player
        local_host.stop(playerid)
        local_host.executeJSON('Playlist.Clear','{"playlistid": ' + playerid + '}')
            
        if(keep_playing):
            #unpause
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
            
