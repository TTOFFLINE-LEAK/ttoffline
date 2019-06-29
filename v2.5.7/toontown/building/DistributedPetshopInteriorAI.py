from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPetshopInteriorAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPetshopInteriorAI')

    def __init__(self, block, air, zoneId):
        DistributedObjectAI.__init__(self, air)
        self.air = air
        self.zoneId = zoneId
        self.block = block

    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def getZoneIdAndBlock(self):
        return [
         self.zoneId, self.block]