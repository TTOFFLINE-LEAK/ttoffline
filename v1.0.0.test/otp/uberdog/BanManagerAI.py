from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
import json

class BanManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerAI')

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

    def sendBan(self, sender=0, avId=0, banType='hwId', duration=0, reason='Unknown'):
        self.sendUpdate('handleBan', [sender, avId, banType, duration, reason])

    def sendKick(self, avId=0, reason='N/A', silent=0):
        self.sendUpdate('handleKick', [avId, reason, silent])

    def openFile(self):
        with open(self.filename, 'r') as (file):
            self.jsonData = json.load(file)
            file.close()
        return self.jsonData