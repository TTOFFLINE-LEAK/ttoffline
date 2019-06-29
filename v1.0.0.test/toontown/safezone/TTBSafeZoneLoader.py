from pandac.PandaModules import *
import SafeZoneLoader, TTBPlayground

class TTBSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TTBPlayground.TTBPlayground
        self.musicFile = 'phase_4/audio/bgm/TC_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        self.dnaFile = 'phase_14/dna/toontown_central_beta_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_4/dna/storage_TT_sz.dna'