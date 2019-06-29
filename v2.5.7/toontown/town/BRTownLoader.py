import TownLoader, BRStreet
from toontown.suit import Suit

class BRTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = BRStreet.BRStreet
        self.musicFile = 'phase_8/audio/bgm/TB_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/TB_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_BR_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False):
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/TB_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/the_burrrgh_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)