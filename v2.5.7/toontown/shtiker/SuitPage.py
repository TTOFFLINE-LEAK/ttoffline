import random
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from otp.nametag.ChatBalloon import ChatBalloon
from otp.otpbase import OTPLocalizer
from toontown.battle import SuitBattleGlobals
from toontown.battle import BattleProps
from toontown.suit import Suit
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from CogPageGlobals import *
import ShtikerPage, SummonCogDialog
SCALE_FACTOR = 1.5
RADAR_DELAY = 0.2
BUILDING_RADAR_POS = (0.375, 0.065, -0.225, -0.5)
PANEL_COLORS = (Vec4(0.8, 0.78, 0.77, 1),
 Vec4(0.75, 0.78, 0.8, 1),
 Vec4(0.75, 0.82, 0.79, 1),
 Vec4(0.825, 0.76, 0.77, 1))
PANEL_COLORS_COMPLETE1 = (Vec4(0.7, 0.725, 0.545, 1),
 Vec4(0.625, 0.725, 0.65, 1),
 Vec4(0.6, 0.75, 0.525, 1),
 Vec4(0.675, 0.675, 0.55, 1))
PANEL_COLORS_COMPLETE2 = (Vec4(0.9, 0.725, 0.32, 1),
 Vec4(0.825, 0.725, 0.45, 1),
 Vec4(0.8, 0.75, 0.325, 1),
 Vec4(0.875, 0.675, 0.35, 1))
PREVIOUS_SUIT_POS = -0.7
NEXT_SUIT_POS = 0.7
SUIT_Z = -0.6
ACT_DELAY_MIN = 8.0
ACT_DELAY_MAX = 15.0
SUIT_DIAL_DICT = {'murmur': 'phase_3.5/audio/dial/COG_VO_murmur.ogg', 
   'statement': 'phase_3.5/audio/dial/COG_VO_statement.ogg', 
   'question': 'phase_3.5/audio/dial/COG_VO_question.ogg', 
   'grunt': 'phase_3.5/audio/dial/COG_VO_grunt.ogg'}
SKEL_DIAL_DICT = {'murmur': 'phase_5/audio/sfx/Skel_COG_VO_murmur.ogg', 
   'statement': 'phase_5/audio/sfx/Skel_COG_VO_statement.ogg', 
   'question': 'phase_5/audio/sfx/Skel_COG_VO_question.ogg', 
   'grunt': 'phase_5/audio/sfx/Skel_COG_VO_grunt.ogg'}

class SuitPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.SuitPageTitle, text_scale=0.1, text_pos=(0.04,
                                                                                                                     0.625), textMayChange=0)
        self.suitName = OnscreenText(parent=self, text='', scale=0.1, pos=(0.04, 0.5), font=ToontownGlobals.getSuitFont())
        self.suitInfo = OnscreenText(parent=self, text='', scale=0.05, pos=(0.04, 0.4), font=ToontownGlobals.getSuitFont())
        self.radarButtons = []
        self.suitChatBalloon = None
        self.suitChat = None
        self.suitChatNP = None
        self.suitSound = None
        self.currentSuit = None
        self.nextSuit = None
        self.previousSuit = None
        self.selectedSuit = 0
        self.currentDept = 0
        self.deptList = self.generateDeptList()
        self.moveSeq = None
        self.actSeq = None
        matGUI = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        guiNextUp = matGUI.find('**/tt_t_gui_mat_nextUp')
        guiNextDown = matGUI.find('**/tt_t_gui_mat_nextDown')
        guiNextDisabled = matGUI.find('**/tt_t_gui_mat_nextDisabled')
        self.guiNextButton = DirectButton(parent=self, relief=None, image=(guiNextUp,
         guiNextDown,
         guiNextUp,
         guiNextDisabled), image_scale=(0.3, 0.3, 0.3), image1_scale=(0.35, 0.35, 0.35), image2_scale=(0.35,
                                                                                                       0.35,
                                                                                                       0.35), pos=(1.165,
                                                                                                                   0,
                                                                                                                   -0.018), command=self.goForwards, text=('',
         TTLocalizer.MakeAToonNext,
         TTLocalizer.MakeAToonNext,
         ''), text_font=ToontownGlobals.getSuitFont(), text_scale=TTLocalizer.MATguiNextButton, text_pos=(0,
                                                                                                          0.115), text_fg=(0.5,
                                                                                                                           0.5,
                                                                                                                           0.5,
                                                                                                                           1), text_shadow=(0,
                                                                                                                                            0,
                                                                                                                                            0,
                                                                                                                                            1))
        self.guiNextButton.setPos(0.498, 0, 0)
        self.guiNextButton.reparentTo(aspect2d)
        self.guiNextButton.stash()
        self.guiLastButton = DirectButton(parent=self, relief=None, image=(guiNextUp,
         guiNextDown,
         guiNextUp,
         guiNextDown), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-0.3, 0.3,
                                                                            0.3), image1_scale=(-0.35,
                                                                                                0.35,
                                                                                                0.35), image2_scale=(-0.35,
                                                                                                                     0.35,
                                                                                                                     0.35), pos=(0.825,
                                                                                                                                 0,
                                                                                                                                 -0.018), command=self.goBackwards, text=('',
         TTLocalizer.MakeAToonLast,
         TTLocalizer.MakeAToonLast,
         ''), text_font=ToontownGlobals.getSuitFont(), text_scale=0.08, text_pos=(0,
                                                                                  0.115), text_fg=(0.5,
                                                                                                   0.5,
                                                                                                   0.5,
                                                                                                   1), text_shadow=(0,
                                                                                                                    0,
                                                                                                                    0,
                                                                                                                    1))
        self.guiLastButton.setPos(-0.498, 0, 0)
        self.guiLastButton.reparentTo(aspect2d)
        self.guiLastButton.stash()
        self.guiNextDept = DirectButton(parent=self, relief=None, image=(guiNextUp,
         guiNextDown,
         guiNextUp,
         guiNextDisabled), image_scale=(0.1, 0.1, 0.1), image1_scale=(0.15, 0.15, 0.15), image2_scale=(0.15,
                                                                                                       0.15,
                                                                                                       0.15), pos=(1.165,
                                                                                                                   0,
                                                                                                                   -0.018), command=self.nextDept, text=('',
         TTLocalizer.MakeAToonNext,
         TTLocalizer.MakeAToonNext,
         ''), text_font=ToontownGlobals.getSuitFont(), text_scale=TTLocalizer.MATguiNextButton / 2, text_pos=(0,
                                                                                                              0.08), text_fg=(0.5,
                                                                                                                              0.5,
                                                                                                                              0.5,
                                                                                                                              1), text_shadow=(0,
                                                                                                                                               0,
                                                                                                                                               0,
                                                                                                                                               1))
        self.guiNextDept.setPos(-0.5, 0, 0.625)
        self.guiNextDept.reparentTo(aspect2d)
        self.guiNextDept.stash()
        self.guiLastDept = DirectButton(parent=self, relief=None, image=(guiNextUp,
         guiNextDown,
         guiNextUp,
         guiNextDown), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-0.1, 0.1,
                                                                            0.1), image1_scale=(-0.15,
                                                                                                0.15,
                                                                                                0.15), image2_scale=(-0.15,
                                                                                                                     0.15,
                                                                                                                     0.15), pos=(0.825,
                                                                                                                                 0,
                                                                                                                                 -0.018), command=self.prevDept, text=('',
         TTLocalizer.MakeAToonLast,
         TTLocalizer.MakeAToonLast,
         ''), text_font=ToontownGlobals.getSuitFont(), text_scale=0.04, text_pos=(0,
                                                                                  0.08), text_fg=(0.5,
                                                                                                  0.5,
                                                                                                  0.5,
                                                                                                  1), text_shadow=(0,
                                                                                                                   0,
                                                                                                                   0,
                                                                                                                   1))
        self.guiLastDept.setPos(-0.75, 0, 0.625)
        self.guiLastDept.reparentTo(aspect2d)
        self.guiLastDept.stash()
        self.iconMdl = loader.loadModel('phase_3/models/gui/cog_icons')
        self.icons = [self.iconMdl.find('**/CorpIcon'), self.iconMdl.find('**/LegalIcon'), self.iconMdl.find('**/MoneyIcon'), self.iconMdl.find('**/SalesIcon')]
        for icon in self.icons:
            icon.reparentTo(aspect2d)
            icon.setScale(0.1)
            icon.setPos(-0.625, 0, 0.625)
            icon.stash()

        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okButtonList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
        gui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        iconGeom = gui.find('**/summons')
        summonButton = DirectButton(parent=self, pos=(0.825, 0.0, -0.018), scale=0.1, relief=None, state=DGG.NORMAL, image=okButtonList, image_scale=13.0, geom=iconGeom, geom_scale=0.7, text=('',
         TTLocalizer.IssueSummons,
         TTLocalizer.IssueSummons,
         ''), text_font=ToontownGlobals.getSuitFont(), text_scale=0.5, text_fg=(0.5,
                                                                                0.5,
                                                                                0.5,
                                                                                1), text_shadow=(0,
                                                                                                 0,
                                                                                                 0,
                                                                                                 1), text_pos=(0,
                                                                                                               0.5), command=self.summonButtonPressed, extraArgs=[])
        self.summonButton = summonButton
        self.summonButton.setPos(0.625, 0, 0.5)
        self.summonButton.stash()
        return

    def generateDeptList(self):
        if base.localAvatar.rankNinesUnlocked[self.currentDept]:
            return SuitDNA.suitHeadTypes[self.currentDept * SuitDNA.suitsPerDept:self.currentDept * SuitDNA.suitsPerDept + SuitDNA.suitsPerDept]
        return SuitDNA.suitHeadTypes[self.currentDept * SuitDNA.suitsPerDept:self.currentDept * SuitDNA.suitsPerDept + SuitDNA.normalSuits]

    def getNextSuit(self):
        if base.localAvatar.rankNinesUnlocked[self.currentDept]:
            return min((self.selectedSuit + 1) % SuitDNA.suitsPerDept, SuitDNA.suitsPerDept)
        return min((self.selectedSuit + 1) % SuitDNA.normalSuits, SuitDNA.normalSuits)

    def getPreviousSuit(self):
        if base.localAvatar.rankNinesUnlocked[self.currentDept]:
            if self.selectedSuit - 1 < 0:
                return SuitDNA.suitsPerDept - 1
            return self.selectedSuit - 1
        else:
            if self.selectedSuit - 1 < 0:
                return SuitDNA.normalSuits - 1
            return self.selectedSuit - 1

    def unload(self):
        self.ignoreAll()
        self.title.destroy()
        self.suitName.destroy()
        self.suitInfo.destroy()
        if self.suitChatBalloon:
            self.suitChatBalloon.removeNode()
            del self.suitChatBalloon
        if self.suitChatNP:
            self.suitChatNP.removeNode()
            del self.suitChatNP
        if hasattr(self, 'suitChat'):
            del self.suitChat
        if hasattr(self, 'suitSound'):
            del self.suitSound
        if self.summonButton:
            self.summonButton.destroy()
        self.iconMdl.removeNode()
        self.guiNextButton.destroy()
        self.guiLastButton.destroy()
        self.guiNextDept.destroy()
        self.guiLastDept.destroy()
        del self.guiNextButton
        del self.guiLastButton
        del self.guiNextDept
        del self.guiLastDept
        del self.icons
        ShtikerPage.ShtikerPage.unload(self)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self.currentSuit = self.makeCog(self.selectedSuit)
        currentKnown = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.currentSuit.setColorScale(currentKnown, currentKnown, currentKnown, 1)
        self.updateInformation()
        prevSuitIdx = self.getPreviousSuit()
        self.previousSuit = self.makeCog(prevSuitIdx)
        self.previousSuit.setX(PREVIOUS_SUIT_POS)
        prevKnown = base.localAvatar.cogCounts[(prevSuitIdx + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.previousSuit.setColorScale(prevKnown, prevKnown, prevKnown, 0)
        nextSuitIdx = self.getNextSuit()
        self.nextSuit = self.makeCog(nextSuitIdx)
        self.nextSuit.setX(NEXT_SUIT_POS)
        nextKnown = base.localAvatar.cogCounts[(nextSuitIdx + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.nextSuit.setColorScale(nextKnown, nextKnown, nextKnown, 0)
        self.guiNextButton.unstash()
        self.guiLastButton.unstash()
        self.guiNextDept.unstash()
        self.guiLastDept.unstash()
        self.icons[self.currentDept].unstash()
        taskMgr.doMethodLater(1, self.getRadar, 'UpdateTask')
        self.startAction()
        if base.localAvatar.hasCogSummons(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept):
            self.summonButton.unstash()
        else:
            self.summonButton.stash()

    def exit(self):
        taskMgr.remove('UpdateTask')
        taskMgr.remove('ActionTask')
        self.ignoreAll()
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None
        if self.actSeq:
            self.actSeq.finish()
            self.actSeq = None
        if self.currentSuit:
            self.currentSuit.cleanup()
            self.currentSuit.delete()
            self.currentSuit = None
        if self.nextSuit:
            self.nextSuit.cleanup()
            self.nextSuit.delete()
            self.nextSuit = None
        if self.previousSuit:
            self.previousSuit.cleanup()
            self.previousSuit.delete()
            self.previousSuit = None
        self.guiNextButton.stash()
        self.guiLastButton.stash()
        self.guiNextDept.stash()
        self.guiLastDept.stash()
        self.icons[self.currentDept].stash()
        self.summonButton.stash()
        ShtikerPage.ShtikerPage.exit(self)
        return

    def makeCog(self, idx):
        idx = max(idx, 0)
        if idx > len(self.deptList) - 1:
            idx = 0
        newSuit = Suit.Suit()
        newSuit.dna = SuitDNA.SuitDNA()
        newSuit.dna.newSuit(self.deptList[idx])
        newSuit.setDNA(newSuit.dna)
        newSuit.reparentTo(self)
        newSuit.loop('neutral')
        newSuit.setScale(0.1)
        newSuit.setBin('unsorted', 0, 1)
        newSuit.setDepthTest(True)
        newSuit.setDepthWrite(True)
        newSuit.setZ(SUIT_Z)
        newSuit.setH(180)
        newSuit.setTransparency(1)
        return newSuit

    def doAction(self, task):
        if not self.currentSuit:
            return Task.done
        if self.actSeq:
            self.actSeq.finish()
        self.setSuitChat(SuitBattleGlobals.getFaceoffTaunt(self.currentSuit.dna.name, 0, True))
        anim = random.choice(['victory', 'slip-backward', 'slip-forward', 'reach', 'hypnotized', 'lured', 'neutral', 'neutral'])
        self.actSeq = Sequence(ActorInterval(self.currentSuit, anim), Func(self.currentSuit.loop, 'neutral'))
        self.actSeq.start()
        task.delayTime = random.randrange(ACT_DELAY_MIN, ACT_DELAY_MAX)
        return Task.again

    def setSuitChat(self, str, timeout=10):
        self.clearSuitChat()
        searchString = str.lower()
        stringLength = len(str)
        del self.suitSound
        suitIdx = self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept
        if SuitDNA.suitHeadTypes[suitIdx] == 'sf' or SuitDNA.suitHeadTypes[suitIdx] == 'm3':
            dialDict = SKEL_DIAL_DICT
        else:
            dialDict = SUIT_DIAL_DICT
        if searchString.find(OTPLocalizer.DialogSpecial) >= 0:
            self.suitSound = loader.loadSfx(dialDict.get('murmur'))
        else:
            if searchString.find(OTPLocalizer.DialogExclamation) >= 0:
                self.suitSound = loader.loadSfx(dialDict.get('statement'))
            else:
                if searchString.find(OTPLocalizer.DialogQuestion) >= 0:
                    self.suitSound = loader.loadSfx(dialDict.get('question'))
                else:
                    if stringLength <= OTPLocalizer.DialogLength1:
                        self.suitSound = loader.loadSfx(dialDict.get('grunt'))
                    else:
                        if stringLength <= OTPLocalizer.DialogLength2:
                            self.suitSound = loader.loadSfx(dialDict.get('murmur'))
                        else:
                            self.suitSound = loader.loadSfx(dialDict.get('statement'))
        base.playSfx(self.suitSound)
        if not self.suitChatBalloon:
            self.suitChatBalloon = loader.loadModel('phase_3/models/props/chatbox')
        self.suitChat = ChatBalloon(self.suitChatBalloon)
        chatNode = self.suitChat.generate(str, ToontownGlobals.getSuitFont())[0]
        self.suitChatNP = self.currentSuit.attachNewNode(chatNode.node(), 1000)
        self.suitChatNP.setScale(0.325)
        self.suitChatNP.setH(180)
        self.suitChatNP.setPos(0, 0, 0.25 + self.currentSuit.height)
        if timeout:
            taskMgr.doMethodLater(timeout, self.clearSuitChat, 'clearSuitChat')

    def clearSuitChat(self, task=None):
        taskMgr.remove('clearSuitChat')
        if self.suitChatNP:
            self.suitChatNP.removeNode()
            self.suitChatNP = None
            del self.suitChat
        return

    def nextDept(self):
        self.icons[self.currentDept].stash()
        self.currentDept = (self.currentDept + 1) % 4
        self.deptList = self.generateDeptList()
        if self.nextSuit:
            self.nextSuit.cleanup()
            self.nextSuit.delete()
            self.nextSuit = None
        self.nextSuit = self.makeCog(self.selectedSuit)
        self.nextSuit.setPos(NEXT_SUIT_POS, 0, SUIT_Z)
        self.selectedSuit = self.getPreviousSuit()
        self.goForwards(True)
        self.icons[self.currentDept].unstash()
        return

    def prevDept(self):
        self.icons[self.currentDept].stash()
        self.currentDept -= 1
        if self.currentDept < 0:
            self.currentDept = 3
        self.deptList = self.generateDeptList()
        if self.previousSuit:
            self.previousSuit.cleanup()
            self.previousSuit.delete()
            self.previousSuit = None
        self.previousSuit = self.makeCog(self.selectedSuit)
        self.previousSuit.setPos(PREVIOUS_SUIT_POS, 0, SUIT_Z)
        self.selectedSuit = self.getNextSuit()
        self.goBackwards(True)
        self.icons[self.currentDept].unstash()
        return

    def goForwards(self, newPrev=False):
        messenger.send('wakeup')
        if self.moveSeq:
            self.moveSeq.finish()
        if self.actSeq:
            self.actSeq.finish()
        prevSuitKnown = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.selectedSuit = self.getNextSuit()
        suitKnown = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)] != 0
        nextSuitKnown = base.localAvatar.cogCounts[(self.getNextSuit() + self.currentDept * SuitDNA.suitsPerDept)] != 0
        if self.previousSuit:
            self.previousSuit.cleanup()
            self.previousSuit.delete()
            self.previousSuit = None
        self.previousSuit = self.currentSuit
        self.currentSuit = self.nextSuit
        self.nextSuit = self.makeCog(self.getNextSuit())
        self.nextSuit.setPos(NEXT_SUIT_POS, 0, SUIT_Z)
        self.nextSuit.setColorScale(nextSuitKnown, nextSuitKnown, nextSuitKnown, 0)
        self.stopUpdating()
        self.updateInformation()
        taskMgr.doMethodLater(1, self.getRadar, 'UpdateTask')
        self.moveSeq = Sequence(Parallel(self.previousSuit.posInterval(1, (PREVIOUS_SUIT_POS, 0, SUIT_Z)), self.previousSuit.colorScaleInterval(1, (prevSuitKnown, prevSuitKnown, prevSuitKnown, 0)), self.currentSuit.posInterval(1, (0, 0, SUIT_Z)), self.currentSuit.colorScaleInterval(1, (suitKnown, suitKnown, suitKnown, 1))), Func(self.startAction))
        if newPrev:
            self.moveSeq.append(Func(self.newPrev))
        self.moveSeq.start()
        if base.localAvatar.hasCogSummons(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept):
            self.summonButton.unstash()
        else:
            self.summonButton.stash()
        return

    def goBackwards(self, newNext=False):
        messenger.send('wakeup')
        if self.moveSeq:
            self.moveSeq.finish()
        if self.actSeq:
            self.actSeq.finish()
        nextSuitKnown = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.selectedSuit = self.getPreviousSuit()
        suitKnown = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)] != 0
        prevSuitIdx = self.getPreviousSuit()
        prevSuitKnown = base.localAvatar.cogCounts[(prevSuitIdx + self.currentDept * SuitDNA.suitsPerDept)] != 0
        if self.nextSuit:
            self.nextSuit.cleanup()
            self.nextSuit.delete()
            self.nextSuit = None
        self.nextSuit = self.currentSuit
        self.currentSuit = self.previousSuit
        self.previousSuit = self.makeCog(self.getPreviousSuit())
        self.previousSuit.setPos(PREVIOUS_SUIT_POS, 0, SUIT_Z)
        self.previousSuit.setColorScale(prevSuitKnown, prevSuitKnown, prevSuitKnown, 0)
        self.stopUpdating()
        self.updateInformation()
        taskMgr.doMethodLater(1, self.getRadar, 'UpdateTask')
        self.moveSeq = Sequence(Parallel(self.nextSuit.posInterval(1, (NEXT_SUIT_POS, 0, SUIT_Z)), self.nextSuit.colorScaleInterval(1, (nextSuitKnown, nextSuitKnown, nextSuitKnown, 0)), self.currentSuit.posInterval(1, (0, 0, SUIT_Z)), self.currentSuit.colorScaleInterval(1, (suitKnown, suitKnown, suitKnown, 1))), Func(self.startAction))
        if newNext:
            self.moveSeq.append(Func(self.newNext))
        self.moveSeq.start()
        if base.localAvatar.hasCogSummons(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept):
            self.summonButton.unstash()
        else:
            self.summonButton.stash()
        return

    def newNext(self):
        if self.nextSuit:
            self.nextSuit.cleanup()
            self.nextSuit.delete()
            self.nextSuit = None
        self.nextSuit = self.makeCog(self.getNextSuit())
        self.nextSuit.setPos(NEXT_SUIT_POS, 0, SUIT_Z)
        nextSuitKnown = base.localAvatar.cogCounts[(self.getNextSuit() + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.nextSuit.setColorScale(nextSuitKnown, nextSuitKnown, nextSuitKnown, 0)
        return

    def newPrev(self):
        if self.previousSuit:
            self.previousSuit.cleanup()
            self.previousSuit.delete()
            self.previousSuit = None
        self.previousSuit = self.makeCog(self.getPreviousSuit())
        self.previousSuit.setPos(PREVIOUS_SUIT_POS, 0, SUIT_Z)
        prevSuitIdx = self.getPreviousSuit()
        prevKnown = base.localAvatar.cogCounts[(prevSuitIdx + self.currentDept * SuitDNA.suitsPerDept)] != 0
        self.previousSuit.setColorScale(prevKnown, prevKnown, prevKnown, 0)
        return

    def updateInformation(self, cogsFound=-1, bldgsFound=-1):
        count = base.localAvatar.cogCounts[(self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept)]
        try:
            if count == 0:
                suitName = TTLocalizer.SuitPageMystery
                suitNamePlural = TTLocalizer.SuitPageMystery
            else:
                suitName = SuitBattleGlobals.SuitAttributes[self.currentSuit.dna.name]['name']
                suitNamePlural = SuitBattleGlobals.SuitAttributes[self.currentSuit.dna.name]['pluralname']
            if COG_QUOTAS[0][self.selectedSuit] - count > 0:
                suitRadar = TTLocalizer.SuitPageDefeatMoreCogs.format(COG_QUOTAS[0][self.selectedSuit] - count, suitNamePlural)
            else:
                if cogsFound == -1:
                    suitRadar = TTLocalizer.SuitPageLoading
                else:
                    suitRadar = TTLocalizer.SuitPageCogRadar.format(cogsFound, suitNamePlural)
            if COG_QUOTAS[1][self.selectedSuit] - count > 0:
                bldgRadar = TTLocalizer.SuitPageDefeatMoreCogs.format(COG_QUOTAS[1][self.selectedSuit] - count, suitNamePlural)
            else:
                if bldgsFound == -1:
                    bldgRadar = TTLocalizer.SuitPageLoading
                else:
                    hasRadar = True
                    deptCounts = base.localAvatar.cogCounts[self.currentDept * SuitDNA.suitsPerDept:self.currentDept * SuitDNA.suitsPerDept + SuitDNA.suitsPerDept]
                    for cog in xrange(len(deptCounts)):
                        if deptCounts[cog] - COG_QUOTAS[1][cog] < 0:
                            hasRadar = False

                    if hasRadar:
                        bldgRadar = TTLocalizer.SuitPageBuildingRadar.format(bldgsFound, 's' if bldgsFound != 1 else '')
                    else:
                        bldgRadar = TTLocalizer.SuitPageDefeatOtherCogs.format(SuitDNA.getDeptFullnameP(SuitDNA.suitDepts[self.currentDept]))
        except:
            return

        self.suitName.setText(suitName)
        self.suitInfo.setText(('{0}\n{1}\n{2}').format(TTLocalizer.SuitPageQuota % count, suitRadar, bldgRadar))

    def stopUpdating(self):
        taskMgr.remove('UpdateTask')
        taskMgr.remove('ActionTask')

    def startAction(self):
        taskMgr.doMethodLater(random.randrange(ACT_DELAY_MIN, ACT_DELAY_MAX), self.doAction, 'ActionTask')

    def getRadar(self, task):
        deptSize = SuitDNA.suitsPerDept
        if hasattr(base.cr, 'currSuitPlanner'):
            if base.cr.currSuitPlanner != None:
                base.cr.currSuitPlanner.d_suitListQuery()
                self.acceptOnce('suitListResponse', self.__handleSuitListResponse, extraArgs=[self.updateCogRadar()])
                taskMgr.doMethodLater(1.0, self.suitListResponseTimeout, 'suitListResponseTimeout-later', extraArgs=[])
            else:
                self.__handleSuitListResponse(self.updateCogRadar())
        else:
            self.__handleSuitListResponse(self.updateCogRadar())
        return Task.again

    def __handleSuitListResponse(self, numberOfCogs):
        deptSize = SuitDNA.suitsPerDept
        if hasattr(base.cr, 'currSuitPlanner'):
            if base.cr.currSuitPlanner != None:
                base.cr.currSuitPlanner.d_buildingListQuery()
                self.acceptOnce('buildingListResponse', self.__handleBldgListResponse, extraArgs=[numberOfCogs, self.updateBuildingRadar(self.currentDept)])
                taskMgr.doMethodLater(1.0, self.buildingListResponseTimeout, 'buildingListResponseTimeout-later', extraArgs=[numberOfCogs])
            else:
                self.__handleBldgListResponse(numberOfCogs, self.updateBuildingRadar(self.currentDept))
        else:
            self.__handleBldgListResponse(numberOfCogs, self.updateBuildingRadar(self.currentDept))
        return

    def __handleBldgListResponse(self, numberOfCogs, numberOfBldgs):
        self.updateInformation(numberOfCogs, numberOfBldgs)

    def suitListResponseTimeout(self):
        self.__handleSuitListResponse(self.updateCogRadar(1))

    def buildingListResponseTimeout(self, numberOfCogs):
        self.__handleBldgListResponse(numberOfCogs, self.updateBuildingRadar(self.currentDept, 1))

    def summonButtonPressed(self):
        cogIndex = self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept
        self.summonDialog = SummonCogDialog.SummonCogDialog(cogIndex)
        self.summonDialog.load()
        self.accept(self.summonDialog.doneEvent, self.summonDone, extraArgs=[])
        self.summonDialog.enter()

    def summonDone(self):
        if self.summonDialog:
            self.summonDialog.unload()
            self.summonDialog = None
        index = self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept
        if not base.localAvatar.hasCogSummons(index):
            self.summonButton.stash()
        return

    def updateCogRadar(self, timeout=0):
        taskMgr.remove('suitListResponseTimeout-later')
        if not timeout and hasattr(base.cr, 'currSuitPlanner') and base.cr.currSuitPlanner != None:
            cogList = base.cr.currSuitPlanner.suitList
        else:
            cogList = []
        count = 0
        for cog in cogList:
            if cog == self.selectedSuit + self.currentDept * SuitDNA.suitsPerDept:
                count += 1

        return count

    def updateBuildingRadar(self, deptNum, timeout=0):
        taskMgr.remove('buildingListResponseTimeout-later')
        if not timeout and hasattr(base.cr, 'currSuitPlanner') and base.cr.currSuitPlanner != None:
            buildingList = base.cr.currSuitPlanner.buildingList
        else:
            buildingList = [
             0,
             0,
             0,
             0]
        num = buildingList[deptNum]
        return num

    def updatePage(self):
        self.deptList = self.generateDeptList()
        self.updateInformation()