from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.safezone import DistributedBoatAI
from toontown.classicchars import DistributedDonaldDockAI

class DDHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.DonaldsDock
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedDonaldDockAI.DistributedDonaldDockAI
        self.cCharConfigVar = 'want-donald-dock'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info("Creating zone... Donald's Dock")
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)
        boat = DistributedBoatAI.DistributedBoatAI(self.air)
        boat.generateWithRequired(self.zoneId)
        self.addDistObj(boat)