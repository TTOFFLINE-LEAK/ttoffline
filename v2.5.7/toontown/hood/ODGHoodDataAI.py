from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.safezone import ButterflyGlobals
from toontown.safezone.DistributedDGFlowerAI import DistributedDGFlowerAI
from toontown.classicchars import DistributedGoofyAI
from toontown.episodes.DistributedPrologue2EventAI import DistributedPrologue2EventAI
from toontown.episodes.DistributedPrologue3EventAI import DistributedPrologue3EventAI
from toontown.episodes.DistributedPrologue4EventAI import DistributedPrologue4EventAI

class ODGHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.OldDaisyGardens
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        self.accept('avatarExited', self.goAwayOakStreetCogs)
        return

    def startup(self):
        self.notify.info('Creating zone... Old Daisy Gardens')
        HoodDataAI.HoodDataAI.startup(self)
        self.classicChar = None
        self.butterflies = []
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-odg-goofy', True):
                self.createClassicChar()
        if self.air.wantPrologue:
            self.createPrologue2Event()
            self.createPrologue4Event()
            self.createPrologue3Event()
        self.flower = DistributedDGFlowerAI(self.air)
        self.flower.generateWithRequired(self.zoneId)
        self.createButterflies(ButterflyGlobals.DG)
        return

    def createClassicChar(self):
        self.classicChar = DistributedGoofyAI.DistributedGoofyAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()

    def createPrologue2Event(self):
        self.pro2Ev = self.air.doFind('Prologue2Event')
        if self.pro2Ev is None:
            self.pro2Ev = DistributedPrologue2EventAI(self.air)
            self.pro2Ev.generateWithRequired(self.zoneId)
        self.pro2Ev.b_setState('Idle')
        return

    def createPrologue3Event(self):
        self.pro3Ev = self.air.doFind('Prologue3Event')
        if self.pro3Ev is None:
            self.pro3Ev = DistributedPrologue3EventAI(self.air)
            self.pro3Ev.generateWithRequired(ToontownGlobals.OldOakStreet)
        self.pro3Ev.b_setState('Idle')
        return

    def createPrologue4Event(self):
        self.pro4Ev = self.air.doFind('Prologue4Event')
        if self.pro4Ev is None:
            self.pro4Ev = DistributedPrologue4EventAI(self.air)
            self.pro4Ev.generateWithRequired(21834)
        self.pro4Ev.b_setState('Idle')
        return

    def goAwayOakStreetCogs(self, avId):
        if self.air.currentEpisode != 'squirting_flower':
            return
        sp = self.air.suitPlanners.get(ToontownGlobals.OldOakStreet - ToontownGlobals.OldOakStreet % 100)
        sp.flySuits()