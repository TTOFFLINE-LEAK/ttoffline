from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import ButterflyGlobals
from toontown.episodes.DistributedPrologueEventAI import DistributedPrologueEventAI

class SBHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.ScroogeBank
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating prologue...')
        HoodDataAI.HoodDataAI.startup(self)
        self.butterflies = []
        self.proEv = None
        self.createButterflies(ButterflyGlobals.DG)
        if self.air.wantPrologue:
            self.createPrologueEvent()
        return

    def createPrologueEvent(self):
        self.proEv = self.air.doFind('PrologueEvent')
        if self.proEv is None:
            self.proEv = DistributedPrologueEventAI(self.air)
            self.proEv.generateWithRequired(self.zoneId)
        self.proEv.b_setState('Idle')
        return