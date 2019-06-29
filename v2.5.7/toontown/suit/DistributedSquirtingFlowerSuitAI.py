from direct.directnotify import DirectNotifyGlobal
from toontown.suit.DistributedSuitAI import DistributedSuitAI

class DistributedSquirtingFlowerSuitAI(DistributedSuitAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSquirtingFlowerSuitAI')

    def suitFlewAway(self):
        pro3Ev = simbase.air.doFind('Prologue3Event')
        if pro3Ev:
            taskMgr.doMethodLater(0.1, pro3Ev.spawnCog, self.uniqueName('spawnCog'))