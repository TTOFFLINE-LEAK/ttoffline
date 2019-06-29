from panda3d.core import *
import SafeZoneLoader, SBPlayground

class SBSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = SBPlayground.SBPlayground
        self.musicFile = 'phase_14.5/audio/sfx/Silent_sound.ogg'
        self.activityMusicFile = 'phase_14.5/audio/sfx/Silent_sound.ogg'
        self.dnaFile = 'phase_14/dna/tt_dg_moneybin_area.jazz'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_ODG_sz.jazz'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.bird1Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_01.ogg')
        self.bird2Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_02.ogg')
        self.bird3Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_03.ogg')
        self.bird4Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_04.ogg')
        render.setColorScale(1, 1, 1, 1)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.bird1Sound
        del self.bird2Sound
        del self.bird3Sound
        del self.bird4Sound

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)