import TownLoader, DDStreet
from toontown.suit import Suit

class DDTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DDStreet.DDStreet
        self.musicFile = 'phase_6/audio/bgm/DD_SZ.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/DD_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_DD_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False):
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/DD_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(2)
        dnaFile = 'phase_6/dna/donalds_dock_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)

    def unload(self):
        Suit.unloadSuits(2)
        TownLoader.TownLoader.unload(self)

    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)

    def exit(self):
        TownLoader.TownLoader.exit(self)