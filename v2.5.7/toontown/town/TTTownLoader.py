import TownLoader, TTStreet
from toontown.suit import Suit

class TTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.musicFile = 'phase_3.5/audio/bgm/TC_SZ.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False):
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/TTC_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(1)
        dnaFile = 'phase_5/dna/toontown_central_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(1)
        TownLoader.TownLoader.unload(self)