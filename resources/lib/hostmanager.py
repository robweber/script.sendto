import xbmc
import xbmcvfs
import utils
import xml.dom.minidom

class XbmcHost:
    name = ''
    address = ''
    port = 80

    def __init__(self,name,address,port):
        self.name = name
        self.address = address
        self.port = port
        
class HostManager:
    hosts = list()
    
    def __init__(self):
        #try and open the hosts file
        self.readHosts()

    def listHosts(self):
        result = list()
        
        for host in self.hosts:
            result.append(host.name)

        return result

    def getHost(self,index):
        return self.hosts[index]
    
    def readHosts(self):
        data_dir = utils.data_dir()

        if(not xbmcvfs.exists(data_dir)):
            xbmcvfs.mkdir(data_dir)

        try:
            doc = xml.dom.minidom.parse(xbmc.translatePath(data_dir + "hosts.xml"))

            for node in doc.getElementsByTagName("host"):
                self.hosts.append(XbmcHost(str(node.getAttribute("name")),str(node.getAttribute("address")),int(node.getAttribute("port"))))


            #sort the lists
            self.hosts = sorted(self.hosts,key=lambda host: host.name)
            
        except IOError:
            #the file doesn't exist, create it
            doc = xml.dom.minidom.Document()
            rootNode = doc.createElement("hosts")
            doc.appendChild(rootNode)

            #write the file
            f = open(xbmc.translatePath(data_dir + "hosts.xml"),'w')
            doc.writexml(f,"   ")
            f.close()
