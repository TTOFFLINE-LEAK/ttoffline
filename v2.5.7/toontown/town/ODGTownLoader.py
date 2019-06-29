import TownLoader, ODGStreet
from toontown.hood import ZoneUtil
from toontown.suit import Suit
from toontown.toonbase.ToontownGlobals import *
from direct.showbase.Loader import Loader

class ODGTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = ODGStreet.ODGStreet
        if base.cr.scroogeKey == 2:
            self.musicFile = 'phase_14.5/audio/bgm/eggs/SB_bank.ogg'
        else:
            self.musicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.activityMusicFile = 'phase_14.5/audio/sfx/Silent_sound.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_ODG_town.jazz'

    def load(self, zoneId):
        if config.GetBool('custom-battle-music', False) or ZoneUtil.getHoodId(zoneId) == OldDaisyGardens and base.cr.currentEpisode == 'squirting_flower':
            self.battleMusic = base.loader.loadMusic('phase_14.5/audio/bgm/DG_battle.ogg')
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/old_daisys_garden_' + str(self.canonicalBranchZone) + '.jazz'
        self.createHood(dnaFile)
        if hasattr(self, 'loader'):
            tunnel = self.loader.geom.find('**/prop_safe_zone_tunnel_dummy')
            if tunnel:
                tunnel.reparentTo(hidden)

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)