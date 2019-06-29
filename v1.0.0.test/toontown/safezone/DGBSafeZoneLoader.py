from pandac.PandaModules import *
import SafeZoneLoader, DGBPlayground

class DGBSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = DGBPlayground.DGBPlayground
        self.musicFile = 'phase_8/audio/bgm/DG_nbrhood.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.dnaFile = 'phase_14/dna/daisys_garden_beta_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_DG_sz.dna'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.bird1Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_01.ogg')
        self.bird2Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_02.ogg')
        self.bird3Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_03.ogg')
        self.bird4Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_DG_bird_04.ogg')

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.bird1Sound
        del self.bird2Sound
        del self.bird3Sound
        del self.bird4Sound