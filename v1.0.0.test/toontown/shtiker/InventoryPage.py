import ShtikerPage
from toontown.toonbase import ToontownBattleGlobals
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toon import ToonDNA
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class InventoryPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.currentTrackInfo = None
        self.onscreen = 0
        self.currentPage = 0
        self.expanded = False
        self.pages = []
        self.lastInventoryTime = globalClock.getRealTime()
        return

    def load(self):
        gameEffectsInfo = [
         'Username goes here :)',
         str(base.localAvatar.getAccessLevel()),
         TTLocalizer.DiscordOffline if not config.GetBool('mini-server', False) else TTLocalizer.InfoPanelMiniserverMode,
         launcher.getGameServer()]
        color = 'Multicolored'
        if base.localAvatar.style.headColor == base.localAvatar.style.armColor and base.localAvatar.style.headColor == base.localAvatar.style.legColor and base.localAvatar.style.armColor == base.localAvatar.style.legColor and base.localAvatar.style.headColor in TTLocalizer.NumToColor:
            color = TTLocalizer.NumToColor[base.localAvatar.style.headColor]
        toonEffectsInfo = [base.localAvatar.getName(),
         TTLocalizer.AnimalToSpecies[ToonDNA.getSpeciesName(base.localAvatar.style.head)],
         color + ' (%d, %d, %d)' % (base.localAvatar.style.headColor, base.localAvatar.style.armColor, base.localAvatar.style.legColor),
         '0/0',
         TTLocalizer.InfoPanelScale % base.localAvatar.getToonScale(),
         str(base.localAvatar.currentSpeed),
         str(base.localAvatar.cheesyEffect),
         str(base.localAvatar.getCogIndex()),
         '-1',
         '-1',
         '-1']
        battleEffectsInfo = [
         str(base.localAvatar.getImmortalMode()),
         str(base.localAvatar.getInstaKill()),
         str(base.localAvatar.getUnlimitedGags())]
        allEffects = [
         TTLocalizer.InfoPanelGameEffects, TTLocalizer.InfoPanelToonEffects, TTLocalizer.InfoPanelBattleEffects]
        allInfo = [gameEffectsInfo, toonEffectsInfo, battleEffectsInfo]
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.InventoryPageTitle, text_scale=0.12, textMayChange=1, pos=(0,
                                                                                                                                       0,
                                                                                                                                       0.62))
        self.gagFrame = DirectFrame(parent=self, relief=None, pos=(0.1, 0, -0.47), scale=(0.35,
                                                                                          0.35,
                                                                                          0.35), geom=DGG.getDefaultDialogGeom(), geom_color=ToontownGlobals.GlobalDialogColor)
        self.trackInfo = DirectButton(parent=self, relief=None, pos=(-0.4, 0, -0.47), scale=(0.35,
                                                                                             0.35,
                                                                                             0.35), geom=DGG.getDefaultDialogGeom(), geom_scale=(1.4,
                                                                                                                                                 1,
                                                                                                                                                 1), geom_color=ToontownGlobals.GlobalDialogColor, text='', text_wordwrap=11, text_align=TextNode.ALeft, text_scale=0.12, text_pos=(-0.65,
                                                                                                                                                                                                                                                                                    0.3), text_fg=(0.05,
                                                                                                                                                                                                                                                                                                   0.14,
                                                                                                                                                                                                                                                                                                   0.4,
                                                                                                                                                                                                                                                                                                   1), command=self.expandSpellbookInfo)
        self.trackProgress = DirectWaitBar(parent=self.trackInfo, pos=(0, 0, -0.2), relief=DGG.SUNKEN, frameSize=(-0.6,
                                                                                                                  0.6,
                                                                                                                  -0.1,
                                                                                                                  0.1), borderWidth=(0.025,
                                                                                                                                     0.025), scale=1.1, frameColor=(0.4,
                                                                                                                                                                    0.6,
                                                                                                                                                                    0.4,
                                                                                                                                                                    1), barColor=(0.9,
                                                                                                                                                                                  1,
                                                                                                                                                                                  0.7,
                                                                                                                                                                                  1), text='0/0', text_scale=0.15, text_fg=(0.05,
                                                                                                                                                                                                                            0.14,
                                                                                                                                                                                                                            0.4,
                                                                                                                                                                                                                            1), text_align=TextNode.ACenter, text_pos=(0,
                                                                                                                                                                                                                                                                       -0.22))
        self.trackProgress.hide()
        matModel = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        arrow = [ matModel.find('**/tt_t_gui_mat_shuffleArrow' + name) for name in ('Up',
                                                                                    'Down',
                                                                                    'Up',
                                                                                    'Disabled') ]
        self.leftButton = DirectButton(self.trackInfo, relief=None, image_scale=0.7, image=arrow, pos=(-0.455,
                                                                                                       0.0,
                                                                                                       0.3925), command=self.changePage, extraArgs=[-1])
        self.leftButton.hide()
        self.rightButton = DirectButton(self.trackInfo, relief=None, image_scale=(-0.7,
                                                                                  1,
                                                                                  0.7), image=arrow, pos=(0.455,
                                                                                                          0,
                                                                                                          0.3925), command=self.changePage, extraArgs=[1])
        self.rightButton.hide()
        matModel.removeNode()
        circleModel = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        barModel = loader.loadModel('phase_3/models/gui/scroll_bar')
        for title in TTLocalizer.InfoPanelTitles:
            pageNode = DirectScrolledFrame(parent=self.trackInfo, relief=None, frameSize=(-0.65,
                                                                                          0.6,
                                                                                          -0.225,
                                                                                          0.225), canvasSize=(-0.559,
                                                                                                              0.6,
                                                                                                              -0.225,
                                                                                                              0.225), manageScrollBars=0, verticalScroll_geom=barModel, verticalScroll_relief=None, verticalScroll_incButton_relief=None, verticalScroll_decButton_relief=None, verticalScroll_geom_pos=(0,
                                                                                                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                                                                                                         0), verticalScroll_geom_hpr=(0,
                                                                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                                                                      90), verticalScroll_geom_scale=(0.35,
                                                                                                                                                                                                                                                                                                                                                                      1.05,
                                                                                                                                                                                                                                                                                                                                                                      1.05), verticalScroll_thumb_image=circleModel.find('**/tt_t_gui_mat_namePanelCircle'), verticalScroll_resizeThumb=False, horizontalScroll_geom=barModel, horizontalScroll_relief=None, horizontalScroll_incButton_relief=None, horizontalScroll_decButton_relief=None, horizontalScroll_geom_pos=(0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0), horizontalScroll_geom_scale=(0.55,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         1.05,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         1.05), horizontalScroll_thumb_image=circleModel.find('**/tt_t_gui_mat_namePanelCircle'), horizontalScroll_resizeThumb=False, suppressMouse=False)
            pageNode.hide()
            spellbookTitle = DirectButton(parent=pageNode, relief=None, text=title, text_scale=0.12, text_fg=(0.05,
                                                                                                              0.14,
                                                                                                              0.4,
                                                                                                              1), textMayChange=1, pos=(0,
                                                                                                                                        0,
                                                                                                                                        0.35), command=self.changePage, extraArgs=[1])
            self.pages.append(pageNode)

        self.pages[0].show()
        circleModel.removeNode()
        barModel.removeNode()
        effectLabels = []
        for effectList in allEffects:
            for effect in effectList:
                effectIndex = effectList.index(effect)
                effectPageIndex = allEffects.index(effectList)
                infoList = allInfo[effectPageIndex]
                effect = DirectLabel(parent=self.pages[effectPageIndex].getCanvas(), relief=None, text=effect, text_scale=0.07, textMayChange=1, pos=(-0.509, 0.0, 0.2925 - 0.12 * (effectIndex + 1)), text_align=TextNode.ALeft, text_fg=(0.05,
                                                                                                                                                                                                                                           0.14,
                                                                                                                                                                                                                                           0.4,
                                                                                                                                                                                                                                           1))
                effect = DirectLabel(parent=self.pages[effectPageIndex].getCanvas(), relief=None, text=infoList[effectIndex], text_scale=0.07, textMayChange=1, text_fg=(0.05,
                                                                                                                                                                         0.14,
                                                                                                                                                                         0.4,
                                                                                                                                                                         1), pos=(
                 0.309, 0.0, 0.2925 - 0.12 * (effectIndex + 1)), text_align=TextNode.ALeft)
                effectLabels.append(effect)

        jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        self.moneyDisplay = DirectLabel(parent=self, relief=None, pos=(0.55, 0, -0.5), scale=0.8, text=str(base.localAvatar.getMoney()), text_scale=0.18, text_fg=(0.95,
                                                                                                                                                                   0.95,
                                                                                                                                                                   0,
                                                                                                                                                                   1), text_shadow=(0,
                                                                                                                                                                                    0,
                                                                                                                                                                                    0,
                                                                                                                                                                                    1), text_pos=(0,
                                                                                                                                                                                                  -0.1,
                                                                                                                                                                                                  0), image=jarGui.find('**/Jar'), text_font=ToontownGlobals.getSignFont())
        jarGui.removeNode()
        return

    def unload(self):
        del self.title
        ShtikerPage.ShtikerPage.unload(self)

    def expandSpellbookInfo(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.ignore('enterTrackFrame')
            self.ignore('exitTrackFrame')
            pos = (0.0, 0.0, 0.0)
            scale = (1.15, 1.15, 1.15)
            self.leftButton.show()
            self.rightButton.show()
            seq = Parallel(Func(self.trackInfo.wrtReparentTo, aspect2d), LerpScaleInterval(self.trackInfo, 0.3, scale, blendType='noBlend'), LerpPosInterval(self.trackInfo, 0.3, pos, blendType='noBlend'))
        else:
            self.accept('enterTrackFrame', self.updateTrackInfo)
            self.accept('exitTrackFrame', self.clearTrackInfo)
            pos = (-0.4, 0, -0.47)
            scale = (0.35, 0.35, 0.35)
            self.leftButton.hide()
            self.rightButton.hide()
            seq = Parallel(LerpScaleInterval(self.trackInfo, 0.3, scale, blendType='noBlend'), LerpPosInterval(self.trackInfo, 0.3, pos, blendType='noBlend'), Func(self.trackInfo.wrtReparentTo, self))
        seq.start()

    def changePage(self, direction):
        self.pages[self.currentPage].hide()
        nextPage = self.currentPage + 1 * direction
        if nextPage == len(self.pages):
            nextPage = 0
        else:
            if nextPage == -1:
                nextPage = len(self.pages) - 1
        self.currentPage = nextPage
        self.pages[nextPage].show()

    def __moneyChange(self, money):
        self.moneyDisplay['text'] = str(money)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        base.localAvatar.inventory.setActivateMode('book')
        base.localAvatar.inventory.show()
        base.localAvatar.inventory.reparentTo(self)
        self.moneyDisplay['text'] = str(base.localAvatar.getMoney())
        self.accept('enterBookDelete', self.enterDeleteMode)
        self.accept('exitBookDelete', self.exitDeleteMode)
        self.accept('enterTrackFrame', self.updateTrackInfo)
        self.accept('exitTrackFrame', self.clearTrackInfo)
        self.accept(localAvatar.uniqueName('moneyChange'), self.__moneyChange)

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)
        self.clearTrackInfo(self.currentTrackInfo)
        self.ignore('enterBookDelete')
        self.ignore('exitBookDelete')
        self.ignore('enterTrackFrame')
        self.ignore('exitTrackFrame')
        self.ignore(localAvatar.uniqueName('moneyChange'))
        self.makePageWhite(None)
        base.localAvatar.inventory.hide()
        base.localAvatar.inventory.reparentTo(hidden)
        if self.expanded:
            self.expandSpellbookInfo()
        self.exitDeleteMode()
        return

    def enterDeleteMode(self):
        self.title['text'] = TTLocalizer.InventoryPageDeleteTitle
        self.title['text_fg'] = (0, 0, 0, 1)
        self.book['image_color'] = Vec4(1, 1, 0, 1)

    def exitDeleteMode(self):
        self.title['text'] = TTLocalizer.InventoryPageTitle
        self.title['text_fg'] = (0, 0, 0, 1)
        self.book['image_color'] = Vec4(1, 1, 1, 1)

    def updateTrackInfo(self, trackIndex):
        self.currentTrackInfo = trackIndex
        trackName = TextEncoder.upper(ToontownBattleGlobals.Tracks[trackIndex])
        if base.localAvatar.hasTrackAccess(trackIndex):
            self.pages[self.currentPage].hide()
            curExp, nextExp = base.localAvatar.inventory.getCurAndNextExpValues(trackIndex)
            trackText = '%s / %s' % (curExp, nextExp)
            self.trackProgress['range'] = nextExp
            self.trackProgress['value'] = curExp
            if curExp >= ToontownBattleGlobals.regMaxSkill:
                str = TTLocalizer.InventoryPageTrackFull % trackName
                trackText = TTLocalizer.InventoryUberTrackExp % {'nextExp': ToontownBattleGlobals.MaxSkill - curExp}
                self.trackProgress['range'] = ToontownBattleGlobals.UberSkill
                uberCurrExp = curExp - ToontownBattleGlobals.regMaxSkill
                self.trackProgress['value'] = uberCurrExp
            else:
                morePoints = nextExp - curExp
                if morePoints == 1:
                    str = TTLocalizer.InventoryPageSinglePoint % {'trackName': trackName, 'numPoints': morePoints}
                else:
                    str = TTLocalizer.InventoryPagePluralPoints % {'trackName': trackName, 'numPoints': morePoints}
            self.trackInfo['text'] = str
            self.trackProgress['text'] = trackText
            self.trackProgress['frameColor'] = (ToontownBattleGlobals.TrackColors[trackIndex][0] * 0.6,
             ToontownBattleGlobals.TrackColors[trackIndex][1] * 0.6,
             ToontownBattleGlobals.TrackColors[trackIndex][2] * 0.6,
             1)
            self.trackProgress['barColor'] = (ToontownBattleGlobals.TrackColors[trackIndex][0],
             ToontownBattleGlobals.TrackColors[trackIndex][1],
             ToontownBattleGlobals.TrackColors[trackIndex][2],
             1)
            self.trackProgress.show()
        else:
            str = TTLocalizer.InventoryPageNoAccess % trackName
            self.trackInfo['text'] = str
            self.trackProgress.hide()
            self.pages[self.currentPage].hide()

    def clearTrackInfo(self, trackIndex):
        if self.currentTrackInfo == trackIndex:
            self.trackInfo['text'] = ''
            self.trackProgress.hide()
            self.currentTrackInfo = None
            self.pages[self.currentPage].show()
        return

    def acceptOnscreenHooks(self):
        self.accept(ToontownGlobals.InventoryHotkeyOn, self.showInventoryOnscreen)
        self.accept(ToontownGlobals.InventoryHotkeyOff, self.hideInventoryOnscreen)

    def ignoreOnscreenHooks(self):
        self.ignore(ToontownGlobals.InventoryHotkeyOn)
        self.ignore(ToontownGlobals.InventoryHotkeyOff)

    def showInventoryOnscreen(self):
        messenger.send('wakeup')
        timedif = globalClock.getRealTime() - self.lastInventoryTime
        if timedif < 0.7:
            return
        self.lastInventoryTime = globalClock.getRealTime()
        if self.onscreen or base.localAvatar.questPage.onscreen:
            return
        self.onscreen = 1
        base.localAvatar.inventory.setActivateMode('book')
        base.localAvatar.inventory.show()
        base.localAvatar.inventory.reparentTo(self)
        self.moneyDisplay['text'] = str(base.localAvatar.getMoney())
        self.accept('enterTrackFrame', self.updateTrackInfo)
        self.accept('exitTrackFrame', self.clearTrackInfo)
        self.accept(localAvatar.uniqueName('moneyChange'), self.__moneyChange)
        self.reparentTo(aspect2d)
        self.title.hide()
        self.show()

    def hideInventoryOnscreen(self):
        if not self.onscreen:
            return
        self.onscreen = 0
        self.ignore('enterTrackFrame')
        self.ignore('exitTrackFrame')
        self.ignore(localAvatar.uniqueName('moneyChange'))
        base.localAvatar.inventory.hide()
        base.localAvatar.inventory.reparentTo(hidden)
        self.reparentTo(self.book)
        if self.expanded:
            self.expandSpellbookInfo()
        self.title.show()
        self.hide()