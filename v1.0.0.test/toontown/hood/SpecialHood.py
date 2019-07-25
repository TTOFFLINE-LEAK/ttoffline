from pandac.PandaModules import *
import ToonHood
from toontown.town import SPTownLoader
from toontown.safezone import SPSafeZoneLoader
from toontown.toonbase import ToontownGlobals

class SpecialHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ToontownGlobals.ToontownOutskirts
        self.townLoaderClass = SPTownLoader.SPTownLoader
        self.safeZoneLoaderClass = SPSafeZoneLoader.SPSafeZoneLoader
        self.storageDNAFile = 'phase_14/dna/storage_SP.dna'
        self.holidayStorageDNADict = {}
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.titleColor = (1.0, 0.9, 0.5, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.sky.setScale(20.0)
        self.parentFSM.getStateNamed('SpecialHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('SpecialHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        base.camLens.setNearFar(ToontownGlobals.SpecialHoodCameraNear, ToontownGlobals.SpecialHoodCameraFar)

    def exit(self):
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        ToonHood.ToonHood.exit(self)