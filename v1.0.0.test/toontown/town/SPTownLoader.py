import TownLoader, SPStreet
from toontown.suit import Suit

class SPTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = SPStreet.SPStreet
        self.musicFile = 'phase_14.5/audio/bgm/SP_SZ_activity.ogg'
        self.activityMusicFile = 'phase_14.5/audio/bgm/SP_SZ_activity.ogg'
        self.battleMusicFile = 'phase_4/audio/bgm/TC_battle.ogg'
        self.townStorageDNAFile = 'phase_14/dna/storage_SP_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_14/dna/special_hood_' + str(self.canonicalBranchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)