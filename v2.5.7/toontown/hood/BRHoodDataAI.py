from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedPlutoAI, DistributedWesternPlutoAI, DistributedMinnieAI
from toontown.toon import DistributedNPCFishermanAI
from toontown.ai import DistributedPolarPlaceEffectMgrAI

class BRHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.TheBrrrgh
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedPlutoAI.DistributedPlutoAI
        self.cCharClassAF = DistributedMinnieAI.DistributedMinnieAI
        self.cCharClassHW = DistributedWesternPlutoAI.DistributedWesternPlutoAI
        self.cCharConfigVar = 'want-pluto'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... The Brrrgh')
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.POLAR_PLACE_EVENT):
            self.polarPlaceEffectManager = DistributedPolarPlaceEffectMgrAI.DistributedPolarPlaceEffectMgrAI(self.air)
            self.polarPlaceEffectManager.generateWithRequired(3821)