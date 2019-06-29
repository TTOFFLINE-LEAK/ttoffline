from panda3d.core import *
import SafeZoneLoader, TTPlayground, time
from toontown.toonbase import ToontownGlobals

class TTSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TTPlayground.TTPlayground
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_PROPS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.musicFile = 'phase_14.5/audio/bgm/TTC_HW_2017.ogg'
        else:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_CAROLING):
                self.musicFile = 'phase_14.5/audio/bgm/TTC_HD_2016.ogg'
            else:
                self.musicFile = 'phase_4/audio/bgm/TC_nbrhood.ogg'
        self.activityMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.ogg'
        if time.localtime().tm_mon == 12:
            self.dnaFile = 'phase_4/dna/toontown_central_sz_Holiday.jazz'
        else:
            self.dnaFile = 'phase_4/dna/toontown_central_sz.jazz'
        self.safeZoneStorageDNAFile = 'phase_4/dna/storage_TT_sz.jazz'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        if base.cr.newsManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_PROPS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN):
            self.birdSound = map(base.loader.loadSfx, ['phase_4/audio/sfx/MG_sfx_vine_game_bat_flying_lp.ogg', 'phase_4/audio/sfx/MG_sfx_vine_game_bat_shriek_3.ogg'])
        else:
            self.birdSound = map(base.loader.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg', 'phase_4/audio/sfx/SZ_TC_bird2.ogg', 'phase_4/audio/sfx/SZ_TC_bird3.ogg'])

    def unload(self):
        del self.birdSound
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)