from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedTrolleyAI
from toontown.classicchars import DistributedMinnieAI, DistributedWitchMinnieAI, DistributedPlutoAI
from toontown.safezone import DistributedMMPianoAI

class MMHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.MinniesMelodyland
        if zoneId == None:
            zoneId = hoodId
        self.cCharClass = DistributedMinnieAI.DistributedMinnieAI
        self.cCharClassAF = DistributedPlutoAI.DistributedPlutoAI
        self.cCharClassHW = DistributedWitchMinnieAI.DistributedWitchMinnieAI
        self.cCharConfigVar = 'want-pluto'
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info("Creating zone... Minnie's Melodyland")
        HoodDataAI.HoodDataAI.startup(self)
        trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        trolley.generateWithRequired(self.zoneId)
        self.addDistObj(trolley)