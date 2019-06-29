from panda3d.core import *
from toontown.toonbase.ToontownGlobals import *
from direct.directnotify import DirectNotifyGlobal
import Walk
from toontown.toonbase import ToontownGlobals

class PublicWalk(Walk.Walk):
    notify = DirectNotifyGlobal.directNotify.newCategory('PublicWalk')

    def __init__(self, parentFSM, doneEvent):
        Walk.Walk.__init__(self, doneEvent)
        self.parentFSM = parentFSM

    def load(self):
        Walk.Walk.load(self)

    def unload(self):
        Walk.Walk.unload(self)
        del self.parentFSM

    def enter(self, slowWalk=0):
        Walk.Walk.enter(self, slowWalk)
        if hasattr(base.cr, 'inEpisode') and not base.cr.inEpisode:
            if not (base.localAvatar.cameraFollow == 2 or base.localAvatar.zoneId == ToontownGlobals.OldDaisyGardens or base.localAvatar.zoneId == ToontownGlobals.ScroogeBank or base.localAvatar.zoneId == '21834' or base.localAvatar.zoneId == '21821'):
                base.localAvatar.book.showButton()
                self.accept(StickerBookHotkey, self.__handleStickerBookEntry)
                self.accept('enterStickerBook', self.__handleStickerBookEntry)
                self.accept(OptionsPageHotkey, self.__handleOptionsEntry)
        if not (base.localAvatar.cameraFollow == 2 or base.localAvatar.zoneId == ToontownGlobals.OldDaisyGardens or base.localAvatar.zoneId == ToontownGlobals.ScroogeBank or base.localAvatar.zoneId == '21834' or base.localAvatar.zoneId == '21821' or base.cr.currentEpisode == 'short_work' or base.cr.currentEpisode == 'gyro_tale'):
            base.localAvatar.laffMeter.start()
        base.localAvatar.beginAllowPies()

    def exit(self):
        Walk.Walk.exit(self)
        base.localAvatar.book.hideButton()
        self.ignore(StickerBookHotkey)
        self.ignore('enterStickerBook')
        self.ignore(OptionsPageHotkey)
        base.localAvatar.laffMeter.stop()
        base.localAvatar.endAllowPies()

    def __handleStickerBookEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        doneStatus = {}
        doneStatus['mode'] = 'StickerBook'
        messenger.send(self.doneEvent, [doneStatus])
        return

    def __handleOptionsEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        doneStatus = {}
        doneStatus['mode'] = 'Options'
        messenger.send(self.doneEvent, [doneStatus])
        return

    def toggleBook(self, state):
        if state == 'disable':
            self.ignore(StickerBookHotkey)
            self.ignore('enterStickerBook')
            self.ignore(OptionsPageHotkey)
        else:
            if state == 'enable':
                self.accept(StickerBookHotkey, self.__handleStickerBookEntry)
                self.accept('enterStickerBook', self.__handleStickerBookEntry)
                self.accept(OptionsPageHotkey, self.__handleOptionsEntry)