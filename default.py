import xbmc,xbmcgui,xbmcplugin
import sys
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
            
    def listHosts(self):
        context_url = "%s?%s"

        if(len(self.host_manager.hosts) > 0):
            #lists all hosts
            for aHost in self.host_manager.hosts:
                item = xbmcgui.ListItem(aHost.name,aHost.address)
                item.addContextMenuItems([("Add Host","Xbmc.RunPlugin(" + sys.argv[0] + "?mode=1002)")])
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=context_url % (sys.argv[0],"mode=1001&host=" + aHost.address),listitem=item,isFolder=True)
        else:
            #just list the 'add' button
            item = xbmcgui.ListItem("Add Host")
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=context_url % (sys.argv[0],"mode=1002"),listitem=item,isFolder=False)
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)

    def hostInfo(self):
        utils.log(params['host'])
        
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

    def _getInput(self,title):
        result = None
        keyboard = xbmc.Keyboard("",title)
        keyboard.doModal()

        if(keyboard.isConfirmed()):
            result = keyboard.getText()

        return result
            
        
def get_params():
    param={}
    for item in sys.argv:
        #match mode
        match = re.search('mode=(.*)',item)
        if match:
            param['mode'] = match.group(1)
        else:
            param['mode'] = 0

        #match host
        match = re.search('host=(.*)',item)
        if match:
            param['host'] = match.group(1)
            
    return param

mode = 0
params = get_params()

try:
    mode = int(params['mode'])
except:
    pass

if mode == 1000:
    SendTo().run()
else:
    #display gui
    SendGui(params).run()
