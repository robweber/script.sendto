import xbmc
import xbmcvfs
import utils
import xml.dom.minidom
import socket
from commsmanager import LocalComms,RemoteComms

class XbmcHost:
    name = ''
    address = ''
    port = 80
    jsonComm = None
    
    def __init__(self,name,address,port):
        self.name = name
        self.address = address
        self.port = port

        #figure out what kind of comms for this host
        hostname = socket.gethostname()
        host_address = socket.gethostbyname(hostname)

        if(self.address == '127.0.0.1' or self.address == hostname or self.address == host_address):
            #we have a 'local' host
            self.jsonComm = LocalComms()
        else:
            self.jsonComm = RemoteComms(self.address,self.port)

    def executeJSON(self,query,params):
        if(self.jsonComm != None):
            return self.jsonComm.executeJSON(query,params)
        else:
            return None

    def isPlaying(self):
        if(self._getPlayerId() > 0):
            return True
        else:
            return False

    def getPlayingFile(self):
        return "None"

    def _getPlayerId(self):
        #check if this player is actively playing something
        check_playing = self.executeJSON('Player.GetActivePlayers','{}')
        
        if(len(check_playing) > 0):
            return check_playing[0]['playerid']
        else:
            return -1
        
class HostManager:
    hosts = list()
    
    def __init__(self):
        #try and open the hosts file
        self._readHosts()

    def listHosts(self):
        result = list()
        
        for host in self.hosts:
            result.append(host.name)

        return result

    def getHost(self,index):
        return self.hosts[index]

    def addHost(self,aHost):
        self.hosts.append(aHost)
        self._sort()
        self._writeHosts()

    def removeHost(self,index):
        self.hosts.pop(index)
        self._writeHosts()

    def _writeHosts(self):
        data_dir = utils.data_dir()

        try:
            doc = xml.dom.minidom.Document()
            rootNode = doc.createElement("hosts")

            #create the child
            for aHost in self.hosts:
                newChild = doc.createElement("host")
                newChild.setAttribute("name",str(aHost.name))
                newChild.setAttribute("address",str(aHost.address))
                newChild.setAttribute("port",str(aHost.port))
                rootNode.appendChild(newChild)

            doc.appendChild(rootNode)
            #write the file
            f = open(xbmc.translatePath(data_dir + "hosts.xml"),'w')
            doc.writexml(f,"   ")
            f.close()
            

        except IOError:
            utils.log("Error writing hosts file")
    
    def _readHosts(self):
        data_dir = utils.data_dir()

        if(not xbmcvfs.exists(data_dir)):
            xbmcvfs.mkdir(data_dir)

        try:
            doc = xml.dom.minidom.parse(xbmc.translatePath(data_dir + "hosts.xml"))

            for node in doc.getElementsByTagName("host"):
                self.hosts.append(XbmcHost(str(node.getAttribute("name")),str(node.getAttribute("address")),int(node.getAttribute("port"))))

            #sort the lists
            self._sort()
            
        except IOError:
            #the file doesn't exist, create it
            doc = xml.dom.minidom.Document()
            rootNode = doc.createElement("hosts")
            doc.appendChild(rootNode)

            #write the file
            f = open(xbmc.translatePath(data_dir + "hosts.xml"),'w')
            doc.writexml(f,"   ")
            f.close()

    def _sort(self):
        self.hosts = sorted(self.hosts,key=lambda host: host.name)
