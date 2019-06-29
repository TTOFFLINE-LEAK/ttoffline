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
        self.gloveChoice = 0
        self.startColor = 0
        self.nude = False
        return

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        guiRArrowDown = self.gui.find('**/CrtATn_R_Arrow_DN')
        guiRArrowRollover = self.gui.find('**/CrtATn_R_Arrow_RLVR')
        guiRArrowUp = self.gui.find('**/CrtATn_R_Arrow_UP')
        if self.type == CLOTHES_MAKETOON:
            topLPos = (-0.9, 0, 0.1)
            topRPos = (0, 0, 0.1)
            glvLPos = (-0.9, 0, -0.2)
            glvRPos = (0, 0, -0.2)
            botLPos = (-0.9, 0, -0.5)
            botRPos = (0, 0, -0.5)
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
        if self.type == CLOTHES_MAKETOON:
            guiButton = loader.loadModel('phase_3/models/gui/quit_button')
            self.gloveLButton = DirectButton(relief=None, state=DGG.DISABLED, image=(guiRArrowUp, guiRArrowDown,
             guiRArrowRollover, guiRArrowUp), image_scale=(-1, 1, 1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopGloves, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                             0), text_fg=(0.8,
                                                                                                                                                                                          0.1,
                                                                                                                                                                                          0,
                                                                                                                                                                                          1), pos=glvLPos, command=self.__swapGloveColor, extraArgs=[-1])
            self.gloveRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopGloves, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                                     0), text_fg=(0.8,
                                                                                                                                                                                                                                                  0.1,
                                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                                  1), pos=glvRPos, command=self.__swapGloveColor, extraArgs=[1])
            self.gloveLButton.hide()
            self.gloveRButton.hide()
            self.toggleNudeButton = DirectButton(parent=aspect2d, relief=None, image=(
             guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.8,
                                                                                                                                1.1,
                                                                                                                                1.1), pos=(-0.1,
                                                                                                                                           0,
                                                                                                                                           0.55), text=TTLocalizer.ClothesShopNude, text_scale=0.06, text_pos=(0.0,
                                                                                                                                                                                                               -0.02), command=self.__toggleNude)
            self.toggleNudeButton.hide()
            guiButton.removeNode()
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
        if self.type == CLOTHES_MAKETOON:
            self.gloveLButton.destroy()
            self.gloveRButton.destroy()
            self.toggleNudeButton.destroy()
            del self.gloveLButton
            del self.gloveRButton
            del self.toggleNudeButton
        del self.topLButton
        del self.topRButton
        del self.bottomLButton
        del self.bottomRButton

    def showButtons(self):
        self.topLButton.show()
        self.topRButton.show()
        self.bottomLButton.show()
        self.bottomRButton.show()
        if self.type == CLOTHES_MAKETOON:
            self.gloveLButton.show()
            self.gloveRButton.show()
            self.toggleNudeButton.show()
            self.confirmNude()

    def hideButtons(self):
        self.topLButton.hide()
        self.topRButton.hide()
        self.bottomLButton.hide()
        self.bottomRButton.hide()
        if self.type == CLOTHES_MAKETOON:
            self.gloveLButton.hide()
            self.gloveRButton.hide()
            self.toggleNudeButton.hide()

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

    def __swapGloveColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.gloveChoice = (self.gloveChoice + offset) % length
        self.updateGloveScrollButtons(self.gloveChoice, length, self.gloveLButton, self.gloveRButton)
        newColor = colorList[self.gloveChoice]
        self.dna.gloveColor = newColor
        self.toon.swapToonColor(self.dna)

    def updateGloveScrollButtons(self, choice, length, lButton, rButton):
        if choice == (self.startColor - 1) % length:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice == self.startColor % length:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def getGenderColorList(self, dna):
        if self.dna.getGender() == 'm':
            return ToonDNA.defaultBoyColorList
        return ToonDNA.defaultGirlColorList

    def confirmNude(self):
        if self.nude:
            self.toggleNudeButton['text'] = TTLocalizer.ClothesShopClothe
            self.topLButton.hide()
            self.topRButton.hide()
            self.bottomLButton.hide()
            self.bottomRButton.hide()

    def __toggleNude(self):
        if self.nude:
            self.nude = False
            self.toggleNudeButton['text'] = TTLocalizer.ClothesShopNude
            self.topLButton.show()
            self.topRButton.show()
            self.bottomLButton.show()
            self.bottomRButton.show()
            if self.gender == 'm' or self.gender == 'f' and self.girlInShorts:
                self.toon.style.torso += 's'
            else:
                self.toon.style.torso += 'd'
            self.toon.swapToonTorso(self.toon.style.torso, genClothes=1)
            self.toon.loop('neutral')
        else:
            self.nude = True
            self.toggleNudeButton['text'] = TTLocalizer.ClothesShopClothe
            self.topLButton.hide()
            self.topRButton.hide()
            self.bottomLButton.hide()
            self.bottomRButton.hide()
            self.toon.style.torso = self.toon.style.torso[0]
            self.toon.swapToonTorso(self.toon.style.torso, genClothes=0)
            self.toon.loop('neutral')