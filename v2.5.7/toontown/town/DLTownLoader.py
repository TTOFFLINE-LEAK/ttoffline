import TownLoader, DLStreet
from toontown.suit import Suit

class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.musicFile = 'phase_8/audio/bgm/DL_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False):
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/DDL_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)