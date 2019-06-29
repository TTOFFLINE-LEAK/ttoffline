from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.classicchars import DistributedGoofySpeedwayAI, DistributedSuperGoofyAI, DistributedDonaldAI

class GSHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.GoofySpeedway
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedGoofySpeedwayAI.DistributedGoofySpeedwayAI
        self.cCharClassAF = DistributedDonaldAI.DistributedDonaldAI
        self.cCharClassHW = DistributedSuperGoofyAI.DistributedSuperGoofyAI
        self.cCharConfigVar = 'want-goofy'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... Goofy Speedway')
        HoodDataAI.HoodDataAI.startup(self)
        messenger.send('GSHoodSpawned', [self])

    def shutdown(self):
        self.notify.debug('shutting down GSHoodDataAI: %s' % self.zoneId)
        messenger.send('GSHoodDestroyed', [self])
        HoodDataAI.HoodDataAI.shutdown(self)

    def cleanup(self):
        self.notify.debug('cleaning up GSHoodDataAI: %s' % self.zoneId)