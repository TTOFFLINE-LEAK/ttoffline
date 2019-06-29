from pandac.PandaModules import *
import SafeZoneLoader, SPPlayground

class SPSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = SPPlayground.SPPlayground
        self.musicFile = 'phase_14.5/audio/bgm/SP_nbrhood.ogg'
        self.activityMusicFile = 'phase_14.5/audio/bgm/SP_SZ_activity.ogg'
        self.dnaFile = 'phase_14/dna/special_hood_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_14/dna/storage_SP_sz.dna'