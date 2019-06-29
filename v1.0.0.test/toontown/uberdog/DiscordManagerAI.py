from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI

class DiscordManagerAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DiscordManagerAI')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.districtLimit = self.air.districtLimit
        self.districtId = self.air.districtId

    def setDistrictLimit(self, districtLimit):
        self.districtLimit = districtLimit

    def getDistrictLimit(self):
        return self.districtLimit

    def setDistrictId(self, districtId):
        self.districtId = districtId

    def getDistrictId(self):
        return self.districtId