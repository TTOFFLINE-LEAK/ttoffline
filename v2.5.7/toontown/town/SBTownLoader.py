import TownLoader
from toontown.suit import Suit

class SBTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = None
        self.musicFile = 'phase_14.5/audio/sfx/Silent_sound.ogg'
        self.activityMusicFile = 'phase_14.5/audio/sfx/Silent_sound.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_SB_town.jazz'
        return

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_14/dna/tt_dg_moneybin_area' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)