from direct.gui.DirectGui import *
from direct.task import Task
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import *
import random, time

class ToontownLoadingScreen:

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        self.shouldResetHighRise = 0
        self.shouldResetGeneral = 0
        self.firstInit = 1
        self.noOtherLoadGUI = False
        if time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24 and self.noOtherLoadGUI == False:
            self.gui = loader.loadModel('phase_3/models/gui/progress-background-HW_2016')
            self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, text_shadow=(0,
                                                                                                                                          0,
                                                                                                                                          0,
                                                                                                                                          1), textMayChange=1, pos=(0.0,
                                                                                                                                                                    0.0,
                                                                                                                                                                    -0.95), text_fg=(1,
                                                                                                                                                                                     1,
                                                                                                                                                                                     1,
                                                                                                                                                                                     1), text_align=TextNode.ACenter)
            self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0, 0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.4,
                                                                                                                                       0,
                                                                                                                                       0.8,
                                                                                                                                       1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
            self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0, 0, 0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.4,
                                                                                                                                          0,
                                                                                                                                          0.8,
                                                                                                                                          1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
            self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                            0,
                                                                                                            -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.8,
                                                                                                                                                                        0.4,
                                                                                                                                                                        0,
                                                                                                                                                                        1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        else:
            if time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24 and self.noOtherLoadGUI == False:
                self.gui = loader.loadModel('phase_3/models/gui/progress-background-HW_2016')
                self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, text_shadow=(0,
                                                                                                                                              0,
                                                                                                                                              0,
                                                                                                                                              1), textMayChange=1, pos=(0.0,
                                                                                                                                                                        0.0,
                                                                                                                                                                        -0.95), text_fg=(1,
                                                                                                                                                                                         1,
                                                                                                                                                                                         1,
                                                                                                                                                                                         1), text_align=TextNode.ACenter)
                self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0, 0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.4,
                                                                                                                                           0,
                                                                                                                                           0.8,
                                                                                                                                           1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0, 0,
                                                                               0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.4,
                                                                                                                                        0,
                                                                                                                                        0.8,
                                                                                                                                        1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                0,
                                                                                                                -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(1,
                                                                                                                                                                            0.5,
                                                                                                                                                                            0,
                                                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
            else:
                if time.localtime().tm_mon == 12 and self.noOtherLoadGUI == False:
                    self.gui = loader.loadModel('phase_3/models/gui/progress-background-Holiday_2016')
                    self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                                           0.0,
                                                                                                                                                           -0.95), text_fg=(0.1,
                                                                                                                                                                            0.8,
                                                                                                                                                                            0.1,
                                                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0,
                                                                               0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.8,
                                                                                                                                         0.08,
                                                                                                                                         0.08,
                                                                                                                                         1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.72,
                                                                                                                                            0.1,
                                                                                                                                            0.1,
                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                    0,
                                                                                                                    -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.1,
                                                                                                                                                                                0.8,
                                                                                                                                                                                0.1,
                                                                                                                                                                                1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                else:
                    self.gui = loader.loadModel('phase_3/models/gui/progress-background')
                    self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                                           0.0,
                                                                                                                                                           -0.95), text_fg=(0.4,
                                                                                                                                                                            0.3,
                                                                                                                                                                            0.2,
                                                                                                                                                                            1), text_align=TextNode.ACenter)
                    self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0,
                                                                               0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.952,
                                                                                                                                         0.631,
                                                                                                                                         0.007,
                                                                                                                                         1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.968,
                                                                                                                                            0.917,
                                                                                                                                            0.131,
                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
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
        self.head = None
        if config.GetBool('want-placer-panel', False):
            self.gui.place()
        return

    def highRiseReset(self):
        if self.shouldResetHighRise == 1:
            self.shouldResetHighRise = 0
        else:
            if self.shouldResetHighRise == 0:
                self.gui = loader.loadModel('phase_3/models/gui/progress-background')
                self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, text_shadow=(0,
                                                                                                                                              0,
                                                                                                                                              0,
                                                                                                                                              1), textMayChange=1, pos=(0.0,
                                                                                                                                                                        0.0,
                                                                                                                                                                        -0.95), text_fg=(1,
                                                                                                                                                                                         1,
                                                                                                                                                                                         1,
                                                                                                                                                                                         1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSuitFont())
                self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0, 0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0,
                                                                                                                                           0,
                                                                                                                                           0,
                                                                                                                                           1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSuitFont())
                self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0, 0,
                                                                               0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.69,
                                                                                                                                        0.69,
                                                                                                                                        0.69,
                                                                                                                                        1), text_shadow=(0,
                                                                                                                                                         0,
                                                                                                                                                         0,
                                                                                                                                                         1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSuitFont())
                self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                0,
                                                                                                                -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.9,
                                                                                                                                                                            0.631,
                                                                                                                                                                            0.007,
                                                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSuitFont())
                self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
                                                                                                               1.06,
                                                                                                               -0.03,
                                                                                                               0.03), pos=(0,
                                                                                                                           0,
                                                                                                                           -0.85), text='')
                self.shouldResetHighRise = 1
        return

    def generalReset(self):
        if self.shouldResetGeneral == 1:
            self.shouldResetGeneral = 0
        else:
            if self.shouldResetGeneral == 0:
                self.noOtherLoadGUI = False
                if time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24 and self.noOtherLoadGUI == False:
                    self.gui = loader.loadModel('phase_3/models/gui/progress-background-HW_2016')
                    self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, text_shadow=(0,
                                                                                                                                                  0,
                                                                                                                                                  0,
                                                                                                                                                  1), textMayChange=1, pos=(0.0,
                                                                                                                                                                            0.0,
                                                                                                                                                                            -0.95), text_fg=(1,
                                                                                                                                                                                             1,
                                                                                                                                                                                             1,
                                                                                                                                                                                             1), text_align=TextNode.ACenter)
                    self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0, 0,
                                                                               0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.4,
                                                                                                                                         0,
                                                                                                                                         0.8,
                                                                                                                                         1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.4,
                                                                                                                                            0,
                                                                                                                                            0.8,
                                                                                                                                            1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                    0,
                                                                                                                    -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.8,
                                                                                                                                                                                0.4,
                                                                                                                                                                                0,
                                                                                                                                                                                1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                else:
                    if time.localtime().tm_mon == 10 and time.localtime().tm_mday >= 24 and self.noOtherLoadGUI == False:
                        self.gui = loader.loadModel('phase_3/models/gui/progress-background-HW_2016')
                        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, text_shadow=(0,
                                                                                                                                                      0,
                                                                                                                                                      0,
                                                                                                                                                      1), textMayChange=1, pos=(0.0,
                                                                                                                                                                                0.0,
                                                                                                                                                                                -0.95), text_fg=(1,
                                                                                                                                                                                                 1,
                                                                                                                                                                                                 1,
                                                                                                                                                                                                 1), text_align=TextNode.ACenter)
                        self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.4,
                                                                                                                                             0,
                                                                                                                                             0.8,
                                                                                                                                             1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                        self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                       0,
                                                                                       0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.4,
                                                                                                                                                0,
                                                                                                                                                0.8,
                                                                                                                                                1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                        0,
                                                                                                                        -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.8,
                                                                                                                                                                                    0.4,
                                                                                                                                                                                    0,
                                                                                                                                                                                    1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                    else:
                        if time.localtime().tm_mon == 12 and self.noOtherLoadGUI == False:
                            self.gui = loader.loadModel('phase_3/models/gui/progress-background-Holiday_2016')
                            self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                                                   0.0,
                                                                                                                                                                   -0.95), text_fg=(0.1,
                                                                                                                                                                                    0.8,
                                                                                                                                                                                    0.1,
                                                                                                                                                                                    1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                       0,
                                                                                       0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.8,
                                                                                                                                                 0.08,
                                                                                                                                                 0.08,
                                                                                                                                                 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                           0,
                                                                                           0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.72,
                                                                                                                                                    0.1,
                                                                                                                                                    0.1,
                                                                                                                                                    1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                            0,
                                                                                                                            -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.1,
                                                                                                                                                                                        0.8,
                                                                                                                                                                                        0.1,
                                                                                                                                                                                        1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                        else:
                            self.gui = loader.loadModel('phase_3/models/gui/progress-background')
                            self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent=self.gui, relief=None, text='', text_scale=0.05, textMayChange=1, pos=(0.0,
                                                                                                                                                                   0.0,
                                                                                                                                                                   -0.95), text_fg=(0.4,
                                                                                                                                                                                    0.3,
                                                                                                                                                                                    0.2,
                                                                                                                                                                                    1), text_align=TextNode.ACenter)
                            self.toon = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                       0,
                                                                                       0.8), text='', textMayChange=1, text_scale=0.17, text_fg=(0.952,
                                                                                                                                                 0.631,
                                                                                                                                                 0.007,
                                                                                                                                                 1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.starring = DirectLabel(parent=self.gui, relief=None, pos=(0,
                                                                                           0,
                                                                                           0.7), text='', textMayChange=1, text_scale=0.1, text_fg=(0.968,
                                                                                                                                                    0.917,
                                                                                                                                                    0.131,
                                                                                                                                                    1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                            self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0,
                                                                                                                            0,
                                                                                                                            -0.77), text='', textMayChange=1, text_scale=0.15, text_fg=(0.9,
                                                                                                                                                                                        0.631,
                                                                                                                                                                                        0.007,
                                                                                                                                                                                        1), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
                self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-1.06,
                                                                                                               1.06,
                                                                                                               -0.03,
                                                                                                               0.03), pos=(0,
                                                                                                                           0,
                                                                                                                           -0.85), text='')
                self.head = None
                self.shouldResetGeneral = 1
        return

    def destroy(self):
        self.tip.destroy()
        self.toon.destroy()
        self.starring.destroy()
        self.title.destroy()
        self.waitBar.destroy()
        self.gui.removeNode()

    def getTip(self, tipCategory):
        if hasattr(base, 'cr') and base.cr.currentEpisode == 'short_work':
            return TTLocalizer.TipTitleCH + random.choice(TTLocalizer.TipDictCH.get(tipCategory))
        if time.localtime().tm_mon == 3 and time.localtime().tm_mday >= 31 or time.localtime().tm_mon == 4 and time.localtime().tm_mday <= 5:
            return TTLocalizer.TipTitleAF + random.choice(TTLocalizer.TipDictAF.get(tipCategory))
        return TTLocalizer.TipTitle + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def resetBackground(self):
        base.setBackgroundColor(ToontownGlobals.DefaultBackgroundColor)

    def begin(self, range, label, gui, tipCategory):
        self.waitBar['range'] = range
        self.tip['text'] = self.getTip(tipCategory)
        self.title['text'] = label
        if hasattr(base, 'cr') and base.cr.currentEpisode == 'short_work':
            self.title['text_fg'] = (0, 0, 0, 1)
            self.title['text_scale'] = 0.1169
        self.__count = 0
        self.__expectedCount = range
        if gui:
            base.setBackgroundColor(Vec4(0.952, 0.796, 0.317, 1))
            if base.localAvatarStyle:
                self.toon['text'] = base.localAvatarName
                self.starring['text'] = TTLocalizer.StarringIn
                if base.cr.oranges:
                    from toontown.suit import Suit, SuitDNA
                    avatar = Suit.Suit()
                    avatar.dna = SuitDNA.SuitDNA()
                    suitIndex = base.localAvatarStyle.armColor % 8 + SuitDNA.suitsPerDept * (base.localAvatarStyle.sleeveTex % 5)
                    avatar.dna.newSuit(SuitDNA.suitHeadTypes[suitIndex])
                    avatar.setDNA(avatar.dna)
                    self.head = self.gui.attachNewNode('head')
                    for part in avatar.headParts:
                        copyPart = part.copyTo(self.head)
                        copyPart.setDepthTest(1)
                        copyPart.setDepthWrite(1)

                    p1 = Point3()
                    p2 = Point3()
                    self.head.calcTightBounds(p1, p2)
                    d = p2 - p1
                    biggest = max(d[0], d[1], d[2])
                    s = 0.5 / biggest
                    self.head.setPosHprScale(0, 0, -0.2, 180, 0, 0, s, s, s)
                    avatar.cleanup()
                    avatar.delete()
                elif base.cr.currentEpisode == 'short_work':
                    from toontown.suit import Suit, SuitDNA
                    avatar = Suit.Suit()
                    avatar.dna = SuitDNA.SuitDNA()
                    suitIndex = SuitDNA.suitHeadTypes.index('sc')
                    avatar.dna.newSuit(SuitDNA.suitHeadTypes[suitIndex])
                    avatar.setDNA(avatar.dna)
                    self.head = self.gui.attachNewNode('head')
                    for part in avatar.headParts:
                        copyPart = part.copyTo(self.head)
                        copyPart.setDepthTest(1)
                        copyPart.setDepthWrite(1)

                    p1 = Point3()
                    p2 = Point3()
                    self.head.calcTightBounds(p1, p2)
                    d = p2 - p1
                    biggest = max(d[0], d[1], d[2])
                    s = 0.5 / biggest
                    self.head.setPosHprScale(0, 0, -0.2, 180, 0, 0, s, s, s)
                    avatar.cleanup()
                    avatar.delete()
                else:
                    from toontown.toon import ToonHead
                    self.head = ToonHead.ToonHead()
                    self.head.setupHead(base.localAvatarStyle, forGui=1)
                    self.head.reparentTo(self.gui)
                    self.head.fitAndCenterHead(1, forGui=1)
            self.gui.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
        else:
            self.waitBar.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.title.reparentTo(aspect2dp, DGG.NO_FADE_SORT_INDEX)
            self.gui.reparentTo(hidden)
        self.waitBar.update(self.__count)
        self.firstInit = 0

    def endStuff(self):
        self.waitBar.finish()
        self.waitBar.reparentTo(self.gui)
        self.toon.reparentTo(self.gui)
        self.starring.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        self.resetBackground()
        if self.head:
            if base.cr.oranges:
                self.head.removeNode()
            else:
                if base.cr.currentEpisode == 'short_work':
                    self.head.removeNode()
                else:
                    self.head.delete()
            self.head = None
        return (self.__expectedCount, self.__count)

    def end(self):
        if base.cr.loadingStuff == 69:
            seq = Sequence(Wait(2.5), Func(self.endStuff))
            seq.start()
        else:
            if base.cr.currentEpisode == 'short_work' or base.cr.currentEpisode == 'gyro_tale':
                chSeq = Sequence(Wait(8), Func(self.endStuff))
                chSeq.start()
            else:
                self.waitBar.finish()
                self.waitBar.reparentTo(self.gui)
                self.toon.reparentTo(self.gui)
                self.starring.reparentTo(self.gui)
                self.title.reparentTo(self.gui)
                self.gui.reparentTo(hidden)
                self.resetBackground()
                if self.head:
                    if base.cr.oranges:
                        self.head.removeNode()
                    else:
                        self.head.delete()
                    self.head = None
                return (self.__expectedCount, self.__count)
        return

    def abort(self):
        self.gui.reparentTo(hidden)
        self.resetBackground()

    def tick(self):
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)