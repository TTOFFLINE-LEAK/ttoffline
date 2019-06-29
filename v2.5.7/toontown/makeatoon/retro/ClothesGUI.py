from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
CLOTHES_MAKETOON = 0
CLOTHES_TAILOR = 1
CLOTHES_CLOSET = 2

class ClothesGUI(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ClothesGUI')

    def __init__(self, type, doneEvent, swapEvent=None):
        StateData.StateData.__init__(self, doneEvent)
        self.type = type
        self.toon = None
        self.swapEvent = swapEvent
        self.gender = '?'
        self.girlInShorts = 0
        self.swappedTorso = 0
        return

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        guiRArrowDown = self.gui.find('**/CrtATn_R_Arrow_DN')
        guiRArrowRollover = self.gui.find('**/CrtATn_R_Arrow_RLVR')
        guiRArrowUp = self.gui.find('**/CrtATn_R_Arrow_UP')
        if self.type == CLOTHES_MAKETOON:
            topLPos = (-0.9, 0, 0)
            topRPos = (0, 0, 0)
            botLPos = (-0.9, 0, -0.4)
            botRPos = (0, 0, -0.4)
        else:
            topLPos = (-0.45, 0, 0.5)
            topRPos = (0.45, 0, 0.5)
            botLPos = (-0.45, 0, 0.1)
            botRPos = (0.45, 0, 0.1)
        self.topLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image_scale=(-1,
                                                                                                                                     1,
                                                                                                                                     1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ClothesShopShirt, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                                 0), text_fg=(0.8,
                                                                                                                                                                                                                                                              0.1,
                                                                                                                                                                                                                                                              0,
                                                                                                                                                                                                                                                              1), pos=topLPos, command=self.swapTop, extraArgs=[-1])
        self.topRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ClothesShopShirt, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                                0), text_fg=(0.8,
                                                                                                                                                                                                                                             0.1,
                                                                                                                                                                                                                                             0,
                                                                                                                                                                                                                                             1), pos=topRPos, command=self.swapTop, extraArgs=[1])
        self.bottomLButton = DirectButton(relief=None, image=(
         guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image_scale=(-1,
                                                                                   1,
                                                                                   1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text='', text_scale=0.0625, text_pos=(0.01,
                                                                                                                                                                     0), text_fg=(0.8,
                                                                                                                                                                                  0.1,
                                                                                                                                                                                  0,
                                                                                                                                                                                  1), pos=botLPos, command=self.swapBottom, extraArgs=[-1])
        self.bottomRButton = DirectButton(relief=None, image=(
         guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text='', text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                    0), text_fg=(0.8,
                                                                                                                                                                 0.1,
                                                                                                                                                                 0,
                                                                                                                                                                 1), pos=botRPos, command=self.swapBottom, extraArgs=[1])
        self.topLButton.hide()
        self.topRButton.hide()
        self.bottomLButton.hide()
        self.bottomRButton.hide()
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.topLButton.destroy()
        self.topRButton.destroy()
        self.bottomLButton.destroy()
        self.bottomRButton.destroy()
        del self.topLButton
        del self.topRButton
        del self.bottomLButton
        del self.bottomRButton

    def showButtons(self):
        self.topLButton.show()
        self.topRButton.show()
        self.bottomLButton.show()
        self.bottomRButton.show()

    def hideButtons(self):
        self.topLButton.hide()
        self.topRButton.hide()
        self.bottomLButton.hide()
        self.bottomRButton.hide()

    def enter(self, toon):
        self.notify.debug('enter')
        base.disableMouse()
        self.toon = toon
        self.setupScrollInterface()

    def exit(self):
        try:
            del self.toon
        except:
            self.notify.warning('ClothesGUI: toon not found')

        self.hideButtons()
        self.ignore('enter')
        self.ignore('next')
        self.ignore('last')

    def setupButtons(self):
        self.girlInShorts = 0
        if self.gender == 'f':
            if self.bottomChoice == -1:
                botTex = self.bottoms[0][0]
            else:
                botTex = self.bottoms[self.bottomChoice][0]
            if ToonDNA.GirlBottoms[botTex][1] == ToonDNA.SHORTS:
                self.girlInShorts = 1
        if self.toon.style.getGender() == 'm':
            self.bottomLButton['text'] = TTLocalizer.ClothesShopShorts
            self.bottomRButton['text'] = TTLocalizer.ClothesShopShorts
        else:
            self.bottomLButton['text'] = TTLocalizer.ClothesShopBottoms
            self.bottomRButton['text'] = TTLocalizer.ClothesShopBottoms
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)

    def swapTop(self, offset):
        length = len(self.tops)
        self.topChoice += offset
        if self.topChoice <= 0:
            self.topChoice = 0
        self.updateScrollButtons(self.topChoice, length, 0, self.topLButton, self.topRButton)
        if self.topChoice < 0 and self.topChoice >= len(self.tops) or len(self.tops[self.topChoice]) != 4:
            self.notify.warning('topChoice index is out of range!')
            return
        self.toon.style.topTex = self.tops[self.topChoice][0]
        self.toon.style.topTexColor = self.tops[self.topChoice][1]
        self.toon.style.sleeveTex = self.tops[self.topChoice][2]
        self.toon.style.sleeveTexColor = self.tops[self.topChoice][3]
        self.toon.generateToonClothes()
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')
        return

    def swapBottom(self, offset):
        length = len(self.bottoms)
        self.bottomChoice += offset
        if self.bottomChoice <= 0:
            self.bottomChoice = 0
        self.updateScrollButtons(self.bottomChoice, length, 0, self.bottomLButton, self.bottomRButton)
        if self.bottomChoice < 0 and self.bottomChoice >= len(self.bottoms) or len(self.bottoms[self.bottomChoice]) != 2:
            self.notify.warning('bottomChoice index is out of range!')
            return
        self.toon.style.botTex = self.bottoms[self.bottomChoice][0]
        self.toon.style.botTexColor = self.bottoms[self.bottomChoice][1]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')
        return

    def updateScrollButtons(self, choice, length, startTex, lButton, rButton):
        if choice >= length - 1:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice <= 0:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def resetClothes(self, style):
        if self.toon:
            self.toon.style.makeFromNetString(style.makeNetString())
            if self.swapEvent != None and self.swappedTorso == 1:
                self.toon.swapToonTorso(self.toon.style.torso, genClothes=0)
                self.toon.generateToonClothes()
                self.toon.loop('neutral', 0)
        return