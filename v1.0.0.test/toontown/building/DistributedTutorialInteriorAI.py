from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedTutorialInteriorAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTutorialInteriorAI')

    def __init__(self, air, zoneId, npcId, block=0):
        DistributedObjectAI.__init__(self, air)
        self.zoneId = zoneId
        self.block = block
        self.npcId = npcId

    def getZoneIdAndBlock(self):
        return (
         self.zoneId, self.block)

    def getTutorialNpcId(self):
        return self.npcId