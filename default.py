import xbmc,xbmcgui,xbmcplugin
import sys
import urlparse
import re
import resources.lib.utils as utils
from resources.lib.sendto import SendTo
from resources.lib.hostmanager import HostManager,XbmcHost

class SendGui:
    params = {}
    host_manager = None
    
    def __init__(self,params):
        self.params = params
        self.host_manager = HostManager()

    def run(self):
        mode = int(params['mode'])
        utils.log(str(params['mode']))
        if(mode == 0):
            self.listHosts()
        elif (mode == 1001):
            self.hostInfo()
        elif(mode == 1002):
            self.addHost()
        elif(mode == 1003):
            self.removeHost()
        elif(mode == 1004):
            self.pullMedia()
        elif(mode == 1005):
            self.sendNotification()
        elif(mode == 1100):
            #create a local and remote host
            local_host = XbmcHost('Local','127.0.0.1','80','','')
            remote_host = XbmcHost('Remote',str(params['address']),str(params['port']),str(params['username']),str(params['password']))
            SendTo().sendTo(local_host,remote_host)
            
    def listHosts(self):
        context_url = "%s?%s"

        if(len(self.host_manager.hosts) > 0):
            #lists all hosts
            index = 0
            for aHost in self.host_manager.hosts:
                item = xbmcgui.ListItem(aHost.name,aHost.address)
                item.addContextMenuItems([(utils.getString(30020),"Xbmc.RunPlugin(%s?%s)" % (sys.argv[0],"mode=1005&host=" + str(index))),(utils.getString(30021), "Xbmc.RunPlugin(%s?%s)" % (sys.argv[0],"mode=1002")),(utils.getString(30022), "Xbmc.RunPlugin(%s?%s)" % (sys.argv[0],'mode=1003&host=' + str(index)))])
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=context_url % (sys.argv[0],"mode=1001&host=" + str(index)),listitem=item,isFolder=True)
                index = index + 1
        else:
            #just list the 'add' button
            item = xbmcgui.ListItem(utils.getString(30021))
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=1002"),listitem=item,isFolder=False)
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)

    def hostInfo(self):
        #get some information about this host
        selectedHost = self.host_manager.getHost(int(params['host']))

        isPlaying = selectedHost.isPlaying()
        
        if(isPlaying == -2):
            item = xbmcgui.ListItem(utils.getString(30024))
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=0"),listitem=item,isFolder=False)
        elif(isPlaying == -1):
            item = xbmcgui.ListItem(utils.getString(30025))
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=0"),listitem=item,isFolder=False)
        else:
            #get properties on the currently playing file
            fileProps = selectedHost.playingProperties()
            
            #get the playlist of playing items
            playingItems = selectedHost.getPlaylist()

            index = 0
            for aItem in playingItems:
                itemLabel = aItem['label']

                if(index == fileProps['position']):
                    itemLabel = "*" + utils.getString(30026) + "* " + itemLabel
                    
                item = xbmcgui.ListItem(itemLabel)
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=1004&host=" + params['host'] + "&item=" + str(index)),listitem=item,isFolder=False)
                index = index + 1
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)
        
    def addHost(self):
        name = None
        address = None
        port = None
        user = None
        password = None
        
        #get the name, address, and port
        name = self._getInput(utils.getString(30027))
        address = self._getInput(utils.getString(30028))
        port = self._getInput(utils.getString(30029))
        user = self._getInput(utils.getString(30042))
        password = self._getInput(utils.getString(30043))

        if(name != None and address != None and port != None):
            aHost = XbmcHost(name,address,int(port),user,password)
            self.host_manager.addHost(aHost)
            xbmc.executebuiltin('Container.Refresh')

    def removeHost(self):
        #remove the host from the hosts file
        self.host_manager.removeHost(int(params['host']))
        xbmc.executebuiltin('Container.Refresh')

    def pullMedia(self):
        host = int(params['host'])
        selectedItem = int(params['item'])
        
        action = xbmcgui.Dialog().select(utils.getString(30030),(utils.getString(30031),utils.getString(30032),utils.getString(30033),utils.getString(30034)))

        remote_host = self.host_manager.getHost(host)
        if(action == 0):
            #do a reverse SendTo
            SendTo().reverse(remote_host)
            xbmc.executebuiltin('Container.Refresh')
        elif(action == 1):
            #start playing only this file
            playingFiles = remote_host.getPlaylist()
            local_host = XbmcHost('Local','127.0.0.1','80','','')
            local_host.playFile(playingFiles[selectedItem]['file'])
        elif(action == 2):
            #pull the whole list but start at this index
            playerid = remote_host.isPlaying()
            playingFiles = remote_host.getPlaylist()
            
            local_host = XbmcHost('Local','127.0.0.1','80','','')

            #send the playerid so we add to the right playlist
            local_host.addItems(playingFiles,playerid)
            local_host.playPosition(selectedItem,playerid)
            
        elif(action == 3):
            #just stop the playing media on this machine
            remote_host.stop()
            xbmc.executebuiltin('Container.Refresh')

    def sendNotification(self):
        remote_host = self.host_manager.getHost(int(params['host']))

        message = self._getInput(utils.getString(30035) + " " + remote_host.name)
        remote_host.sendNotification(message)

    def _getInput(self,title):
        result = None
        keyboard = xbmc.Keyboard("",title)
        keyboard.doModal()

        if(keyboard.isConfirmed()):
            result = keyboard.getText()

        return result
            
        
def get_params():
    param = {}
    try:
        for i in sys.argv:
            args = i
            if(args.startswith('?')):
                args = args[1:]
            param.update(dict(urlparse.parse_qsl(args)))
    except:
        pass
    return param

mode = 0
params = get_params()

try:
    mode = int(params['mode'])
except:
    params['mode'] = mode
    pass

if mode == 1000:
    #start the choosing process
    SendTo().run()
else:
    #display gui
    SendGui(params).run()
