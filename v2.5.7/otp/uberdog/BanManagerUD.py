import json, os
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram

class BanManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.air = air
        self.hwIdByAccountId = {}
        self.accountByHardwareId = {}
        self.file = None
        self.data = {'bans': [{}]}
        self.fileName = 'config/bans.json'
        self.fileSize = 0
        return

    def sendHardwareId(self, hwId):
        accountId = int(self.air.getAccountIdFromSender())
        self.hwIdByAccountId[accountId] = hwId
        self.accountByHardwareId[hwId] = accountId

    def createFile(self):
        with open(self.fileName, 'w+') as (file):
            json.dump(self.data, file, indent=4)
            file.close()

    def openFile(self, fileName):
        with open(fileName, 'r') as (file):
            data = json.load(file)
            file.close()
        return data

    def verifyValidFile(self):
        if os.path.isfile(self.fileName):
            self.fileSize = os.stat(self.fileName).st_size
            if self.fileSize <= 0:
                self.createFile()
            elif not type(self.openFile(self.fileName)) == dict:
                self.createFile()
            elif not self.openFile(self.fileName).get('bans'):
                self.createFile()
        else:
            self.createFile()
        return self.openFile(self.fileName)

    def getActiveBans(self):
        return self.verifyValidFile()['bans']

    def addNewBan(self, avId, accountId, reason):
        datagram = PyDatagram()
        datagram.addServerHeader(self.GetPuppetConnectionChannel(avId), self.air.ourChannel, CLIENTAGENT_EJECT)
        datagram.addUint16(152)
        datagram.addString(str(reason))
        self.air.send(datagram)
        hwId = self.hwIdByAccountId[accountId]
        self.data = self.openFile(self.fileName)
        self.data['bans'][0][hwId] = {'accId': accountId, 'reason': reason}
        with open(self.fileName, 'w') as (file):
            json.dump(self.data, file, indent=4)
            file.close()