from direct.directnotify import DirectNotifyGlobal
from toontown.estate.DistributedLawnDecorAI import DistributedLawnDecorAI

class DistributedGardenBoxAI(DistributedLawnDecorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedGardenBoxAI')

    def setTypeIndex(self, index):
        self.typeIndex = index

    def getTypeIndex(self):
        return self.typeIndex