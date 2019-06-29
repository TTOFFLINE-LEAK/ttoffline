import ToonHood
from toontown.town import TTBTownLoader
from toontown.safezone import TTBSafeZoneLoader
from toontown.toonbase import ToontownGlobals

class TTBetaHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ToontownGlobals.ToontownCentralBeta
        self.townLoaderClass = TTBTownLoader.TTBTownLoader
        self.safeZoneLoaderClass = TTBSafeZoneLoader.TTBSafeZoneLoader
        self.storageDNAFile = 'phase_4/dna/storage_TT.dna'
        self.holidayStorageDNADict = {}
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.9, 0.5, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.sky.setScale(1.5)
        self.parentFSM.getStateNamed('TTBetaHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TTBetaHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        base.camLens.setNearFar(ToontownGlobals.ToontownCentralBetaCameraNear, ToontownGlobals.ToontownCentralBetaCameraFar)

    def exit(self):
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        ToonHood.ToonHood.exit(self)