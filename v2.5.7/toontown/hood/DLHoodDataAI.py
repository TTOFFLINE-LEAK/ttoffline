from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedDonaldAI, DistributedFrankenDonaldAI, DistributedGoofySpeedwayAI
from toontown.safezone import ButterflyGlobals
from toontown.ai.DistributedResistanceEmoteMgrAI import DistributedResistanceEmoteMgrAI

class DLHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.DonaldsDreamland
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedDonaldAI.DistributedDonaldAI
        self.cCharClassAF = DistributedGoofySpeedwayAI.DistributedGoofySpeedwayAI
        self.cCharClassHW = DistributedFrankenDonaldAI.DistributedFrankenDonaldAI
        self.cCharConfigVar = 'want-donald-dreamland'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info("Creating zone... Donald's Dreamland")
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.RESISTANCE_EVENT):
            self.resistanceEmoteMgr = DistributedResistanceEmoteMgrAI(self.air)
            self.resistanceEmoteMgr.generateWithRequired(9720)