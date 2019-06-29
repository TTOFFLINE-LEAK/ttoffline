import ToonHood
from toontown.town import DGBTownLoader
from toontown.safezone import DGBSafeZoneLoader
from toontown.toonbase import ToontownGlobals

class DGBetaHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ToontownGlobals.DaisyGardensBeta
        self.townLoaderClass = DGBTownLoader.DGBTownLoader
        self.safeZoneLoaderClass = DGBSafeZoneLoader.DGBSafeZoneLoader
        self.storageDNAFile = 'phase_8/dna/storage_DG.dna'
        self.holidayStorageDNADict = {}
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.9, 0.5, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.sky.setScale(20.0)
        self.parentFSM.getStateNamed('DGBetaHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DGBetaHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)