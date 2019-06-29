from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedGoofyAI
from toontown.classicchars import DistributedDaisyAI, DistributedSockHopDaisyAI, DistributedMickeyAI
from toontown.safezone import DistributedDGFlowerAI
from toontown.safezone import ButterflyGlobals

class DGHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.DaisyGardens
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedDaisyAI.DistributedDaisyAI
        self.cCharClassAF = DistributedMickeyAI.DistributedMickeyAI
        self.cCharClassHW = DistributedSockHopDaisyAI.DistributedSockHopDaisyAI
        self.cCharConfigVar = 'want-daisy'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... Daisy Gardens')
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)
        flower = DistributedDGFlowerAI.DistributedDGFlowerAI(self.air)
        flower.generateWithRequired(self.zoneId)
        self.addDistObj(flower)
        self.createButterflies(ButterflyGlobals.DG)