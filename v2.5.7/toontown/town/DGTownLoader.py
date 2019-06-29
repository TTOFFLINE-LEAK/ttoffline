import TownLoader, DGStreet
from toontown.suit import Suit

class DGTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DGStreet.DGStreet
        self.musicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        if config.GetBool('want-retro-mode', False):
            self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ_activity_retro.ogg'
        else:
            self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DG_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False):
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/DG_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/daisys_garden_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)