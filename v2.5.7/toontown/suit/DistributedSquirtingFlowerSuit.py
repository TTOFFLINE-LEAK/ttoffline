from direct.directnotify import DirectNotifyGlobal
from toontown.suit.DistributedSuit import DistributedSuit

class DistributedSquirtingFlowerSuit(DistributedSuit):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSquirtingFlowerSuit')

    def enterToSky(self, leg, time):
        DistributedSuit.enterToSky(self, leg, time)
        if base.cr.currentEpisode == 'squrting_flower':
            self.sendUpdate('suitFlewAway')