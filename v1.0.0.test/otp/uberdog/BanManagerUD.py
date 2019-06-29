from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
import os, json

class BanManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.filename = 'bans.json'
        self.hwIdBySender = {}
        self.jsonData = {}
        if not os.path.isfile(self.filename):
            self.notify.info('Creating %s' % self.filename)
            with open(self.filename, 'w+') as (file):
                json.dump({}, file, indent=4)
                file.close()

    def addClient(self, sender, hwId):
        if sender not in self.hwIdBySender:
            self.hwIdBySender[sender] = hwId

    def removeClient(self, sender):
        if sender in self.hwIdBySender:
            self.hwIdBySender[sender] = None
            del self.hwIdBySender[sender]
        return

    def handleBan(self, sender, avId, banType, duration, reason):
        puppet = self.GetPuppetConnectionChannel(avId)
        self.handleKick(avId, reason, 2)
        hwId = self.hwIdBySender[int(sender)]
        if not hwId:
            self.notify.warning('Tried to ban player but hwId is invalid!')
            return
        if hwId in self.jsonData:
            self.notify.warning("Can't ban player that is already banned!")
            return
        self.jsonData[hwId] = {'reason': reason, 'duration': duration, 
           'accId': sender}
        with open(self.filename, 'w') as (file):
            json.dump(self.jsonData, file, indent=4)
            file.close()

    def handleKick(self, avId, reason, silent):
        puppet = self.GetPuppetConnectionChannel(avId)
        if not puppet:
            self.notify.warning('Got an invalid connection for avatar %d' % avId)
            return
        silent2code = {0: 1, 2: 152, 
           3: 155}
        self.dropConnection(puppet, silent2code.get(silent, 1), reason)

    def handleKickAccount(self, accId, reason, silent):
        puppet = self.GetAccountConnectionChannel(accId)
        if not puppet:
            self.notify.warning('Got an invalid connection for account %d' % accId)
            return
        silent2code = {0: 1, 2: 152, 
           3: 155}
        self.dropConnection(puppet, silent2code.get(silent, 1), reason)

    def dropConnection(self, connId, code, reason):
        self.notify.debug('Dropping connection %d code %d for %s' % (connId, code, reason))
        dg = PyDatagram()
        dg.addServerHeader(connId, self.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(code)
        dg.addString(str(reason))
        self.air.send(dg)

    def openFile(self):
        with open(self.filename, 'r') as (file):
            self.jsonData = json.load(file)
            file.close()
        return self.jsonData