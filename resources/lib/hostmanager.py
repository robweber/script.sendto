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
    user = ''
    password = ''
    jsonComm = None
    
    def __init__(self,name,address,port,user,password):
        self.name = name
        self.address = address
        self.port = port
        self.user = user
        self.password = password

        #figure out what kind of comms for this host
        hostname = socket.gethostname()
        host_address = ''
        try:
            host_address = socket.gethostbyname(hostname)
        except:
            #do nothing here, we'll just use a blank string
            pass

        if(self.address == '127.0.0.1' or self.address == hostname or self.address == host_address):
            #we have a 'local' host
            self.jsonComm = LocalComms()
        else:
            self.jsonComm = RemoteComms(self.address,self.port,self.user,self.password)

    def executeJSON(self,query,params):
        if(self.jsonComm != None):
            return self.jsonComm.executeJSON(query,params)
        else:
            return None

    def isPlaying(self):
        return self._getPlayerId()

    def getPlaylist(self,playerid = None):
        result = {}

        if(playerid == None):
            playerid = self._getPlayerId()

        if(playerid >= 0):
            items = self.executeJSON("Playlist.GetItems",'{"playlistid":' + str(playerid) + ',"properties":["file","title"]}')
            result = items['items']

        return result

    def playingProperties(self,playerid=None):
        result = {}

        if(playerid == None):
            playerid = self._getPlayerId()

        if(playerid >= 0):
            result = self.executeJSON("Player.GetProperties",'{"playerid":' + str(playerid) + ', "properties":["percentage","position","speed"]}')

        return result

    def addItems(self,items,playerid):

        #first clear the current playlist
        self.executeJSON('Playlist.Clear','{"playlistid": ' + str(playerid) + '}')

        for aFile in items:
            self.executeJSON('Playlist.Add','{"playlistid":' + str(playerid) + ',"item": {"file": "' + aFile['file'] + '" } }')
        
    def playPosition(self,position,playerid):
        #play the item at a given position in the playlist
        self.executeJSON("Player.Open",'{"item": { "playlistid": ' + str(playerid) + ',"position":' + str(position) + ' } }')

    def playFile(self,aFile,resume=0):
        #play a specific file, resume if sent
        self.executeJSON("Player.Open",'{"item": {"file":"' + aFile + '"},"options":{"resume":' + str(resume) + '}}')

    def seekFile(self,percent,playerid=None):
        if(playerid == None):
            playerid = self._getPlayerId()

        #seek to this point in the file
        self.executeJSON("Player.Seek",'{"playerid":' + str(playerid) + ', "value":' + str(percent) + '}')

    def stop(self,playerid=None):
        if(playerid == None):
            playerid = self._getPlayerId()

        #stop the player
        self.executeJSON('Player.Stop','{"playerid":' + str(playerid) + '}')

    def sendNotification(self,message):
        self.executeJSON('GUI.ShowNotification','{"title":"' + utils.getSetting("notification_title") + '","message":"' + message + '"}')
    
    def _getPlayerId(self):
        utils.log("Finding playerid")
        #check if this player is actively playing something
        check_playing = self.executeJSON('Player.GetActivePlayers','{}')
        
        if(check_playing != None):
            if(len(check_playing) > 0):
                return check_playing[0]['playerid']
            else:
                return -1
        else:
            return -2
        
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
                newChild.setAttribute("user",str(aHost.user))
                newChild.setAttribute("password",str(aHost.password))
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
                self.hosts.append(XbmcHost(str(node.getAttribute("name")),str(node.getAttribute("address")),int(node.getAttribute("port")),str(node.getAttribute("user")),str(node.getAttribute("password"))))

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
