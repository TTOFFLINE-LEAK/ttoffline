import TownLoader, DGBStreet
from toontown.suit import Suit

class DGBTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DGBStreet.DGBStreet
        self.musicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.battleMusicFile = 'phase_8/audio/bgm/DG_battle.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DG_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_14/dna/daisys_garden_beta_' + str(self.canonicalBranchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)