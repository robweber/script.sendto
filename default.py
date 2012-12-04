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
            
    def listHosts(self):
        context_url = "%s?%s"

        if(len(self.host_manager.hosts) > 0):
            #lists all hosts
            index = 0
            for aHost in self.host_manager.hosts:
                item = xbmcgui.ListItem(aHost.name,aHost.address)
                item.addContextMenuItems([("Add Host", "Xbmc.RunPlugin(%s?%s)" % (sys.argv[0],"mode=1002")),("Remove Host", "Xbmc.RunPlugin(%s?%s)" % (sys.argv[0],'mode=1003&host=' + str(index)))])
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=context_url % (sys.argv[0],"mode=1001&host=" + str(index)),listitem=item,isFolder=True)
                index = index + 1
        else:
            #just list the 'add' button
            item = xbmcgui.ListItem("Add Host")
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=1002"),listitem=item,isFolder=False)
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)

    def hostInfo(self):
        #get some information about this host
        selectedHost = self.host_manager.getHost(int(params['host']))

        isPlaying = selectedHost.isPlaying()
        
        if(isPlaying == -2):
            item = xbmcgui.ListItem("Not Running")
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=0"),listitem=item,isFolder=False)
        elif(isPlaying == -1):
            item = xbmcgui.ListItem("Not Playing")
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
                    itemLabel = "*Playing* " + itemLabel
                    
                item = xbmcgui.ListItem(itemLabel)
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="%s?%s" % (sys.argv[0],"mode=1004&host=" + params['host']),listitem=item,isFolder=False)
                index = index + 1
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)
        
    def addHost(self):
        name = None
        address = None
        port = None
        
        #get the name, address, and port
        name = self._getInput("Host Name")
        address = self._getInput("Host Address")
        port = self._getInput("Host Port")

        if(name != None and address != None and port != None):
            aHost = XbmcHost(name,address,int(port))
            self.host_manager.addHost(aHost)
            xbmc.executebuiltin('Container.Refresh')

    def removeHost(self):
        #remove the host from the hosts file
        self.host_manager.removeHost(int(params['host']))
        xbmc.executebuiltin('Container.Refresh')

    def pullMedia(self):
        host = int(params['host'])

        action = xbmcgui.Dialog().select("Choose Action",("Pull now playing","Start playing this file","Copy playlist, start here","Stop Playback"))

        if(action == 0):
            #do a reverse SendTo
            remote_host = self.host_manager.getHost(host)
            SendTo().reverse(remote_host)
        elif(action == 1):
            #start playing only this file
            pass
        elif(action == 2):
            #pull the whole list but start at this index
            pass
        elif(action == 3):
            #just stop the playing media on this machine
            pass

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
    SendTo().run()
else:
    #display gui
    SendGui(params).run()
