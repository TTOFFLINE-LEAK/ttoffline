import TownLoader, TFStreet
from toontown.suit import Suit

class TFTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TFStreet.TFStreet
        self.musicFile = 'phase_6/audio/bgm/GS_Race_RR.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TF_SZ_1.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_TF.jazz'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(1)
        dnaFile = 'phase_6/dna/toonfest_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(1)
        TownLoader.TownLoader.unload(self)