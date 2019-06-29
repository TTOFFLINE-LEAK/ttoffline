from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import *
import random, time

class TTOLoadingScreen:

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        self.firstInit = 0
        self.gui = loader.loadModel('phase_3/models/gui/progress-background-tto')
        self.banner = loader.loadModel('phase_3/models/gui/toon_council').find('**/scroll')
        self.banner.reparentTo(self.gui)
        self.banner.setScale(0.4, 0.4, 0.4)
        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.banner, relief=None, text='', text_scale=TTLocalizer.TLStip, textMayChange=1, pos=(-1.2,
                                                                                                                                                                0.0,
                                                                                                                                                                0.1), text_fg=(0.4,
                                                                                                                                                                               0.3,
                                                                                                                                                                               0.2,
                                                                                                                                                                               1), text_wordwrap=13, text_align=TextNode.ALeft)
        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(-1.06,
                                                                                                        0,
                                                                                                        -0.77), text='', textMayChange=1, text_scale=0.08, text_fg=(0,
                                                                                                                                                                    0,
                                                                                                                                                                    0.5,
                                                                                                                                                                    1), text_align=TextNode.ALeft)
        self.titleTTR = DirectLabel(guiId='ToontownLoadingScreenTitleTTR', parent=self.gui, relief=None, pos=(0,
                                                                                                              0,
                                                                                                              -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(1,
                                                                                                                                                                          0.941,
                                                                                                                                                                          0.09,
                                                                                                                                                                          1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
                                                                                                       1.06,
                                                                                                       -0.03,
                                                                                                       0.03), pos=(0,
                                                                                                                   0,
                                                                                                                   -0.85), text='')
        return

    def destroy(self):
        self.tip.destroy()
        self.title.destroy()
        self.titleTTR.destroy()
        self.waitBar.destroy()
        self.banner.removeNode()
        self.gui.removeNode()

    def getTip(self, tipCategory):
        if time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 8:
            return TTLocalizer.TipTitleAF + '\n' + random.choice(TTLocalizer.TipDictAF.get(tipCategory))
        return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def generalReset(self):
        pass

    def highRiseReset(self):
        pass

    def begin(self, range, label, gui, tipCategory):
        self.waitBar['range'] = range
        if label == 'Loading...' and config.GetBool('want-retro-mode', False):
            self.titleTTR['text'] = label
        else:
            self.title['text'] = label
            self.titleTTR['text'] = ''
        self.tip['text'] = self.getTip(tipCategory)
        self.__count = 0
        self.__expectedCount = range
        if gui:
            self.waitBar.reparentTo(self.gui)
            self.title.reparentTo(self.gui)
            self.titleTTR.reparentTo(self.gui)
            self.gui.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
        else:
            self.waitBar.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.title.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.titleTTR.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.gui.reparentTo(hidden)
        self.waitBar.update(self.__count)

    def endStuff(self):
        self.waitBar.finish()
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.titleTTR.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        return (
         self.__expectedCount, self.__count)

    def end(self):
        if base.cr.loadingStuff == 69:
            seq = Sequence(Wait(2.5), Func(self.endStuff))
            seq.start()
        else:
            if base.cr.currentEpisode == 'short_work':
                chSeq = Sequence(Wait(8), Func(self.endStuff))
                chSeq.start()
            else:
                self.waitBar.finish()
                self.waitBar.reparentTo(self.gui)
                self.title.reparentTo(self.gui)
                self.titleTTR.reparentTo(self.gui)
                self.gui.reparentTo(hidden)
                return (
                 self.__expectedCount, self.__count)

    def abort(self):
        self.gui.reparentTo(hidden)

    def tick(self):
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)