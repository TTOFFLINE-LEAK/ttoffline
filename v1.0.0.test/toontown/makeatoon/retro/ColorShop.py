import random
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import *
from MakeAToonGlobals import *
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer

class ColorShop(StateData.StateData):

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.colorAll = 1
        return

    def getGenderColorList(self, dna):
        if self.dna.getGender() == 'm':
            return ToonDNA.defaultBoyColorList
        else:
            return ToonDNA.defaultGirlColorList

    def enter(self, toon, shopsVisited=[]):
        base.disableMouse()
        self.toon = toon
        self.dna = toon.getStyle()
        colorList = self.getGenderColorList(self.dna)
        if COLORSHOP not in shopsVisited:
            self.headChoice = random.choice(colorList)
            self.armChoice = self.headChoice
            self.legChoice = self.headChoice
            self.startColor = self.headChoice
            self.__swapHeadColor(0)
            self.__swapArmColor(0)
            self.__swapLegColor(0)
            self.allLButton['state'] = DGG.DISABLED
            self.headLButton['state'] = DGG.DISABLED
            self.armLButton['state'] = DGG.DISABLED
            self.legLButton['state'] = DGG.DISABLED
        else:
            try:
                self.headChoice = colorList.index(self.dna.headColor)
                self.armChoice = colorList.index(self.dna.armColor)
                self.legChoice = colorList.index(self.dna.legColor)
            except:
                self.headChoice = random.choice(colorList)
                self.armChoice = self.headChoice
                self.legChoice = self.headChoice
                self.__swapHeadColor(0)
                self.__swapArmColor(0)
                self.__swapLegColor(0)

        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)

    def showButtons(self):
        if self.colorAll:
            self.allLButton.show()
            self.allRButton.show()
            self.headLButton.hide()
            self.headRButton.hide()
            self.armLButton.hide()
            self.armRButton.hide()
            self.legLButton.hide()
            self.legRButton.hide()
        else:
            self.allLButton.hide()
            self.allRButton.hide()
            self.headLButton.show()
            self.headRButton.show()
            self.armLButton.show()
            self.armRButton.show()
            self.legLButton.show()
            self.legRButton.show()
        self.toggleAllButton.show()

    def hideButtons(self):
        self.allLButton.hide()
        self.allRButton.hide()
        self.headLButton.hide()
        self.headRButton.hide()
        self.armLButton.hide()
        self.armRButton.hide()
        self.legLButton.hide()
        self.legRButton.hide()
        self.toggleAllButton.hide()

    def exit(self):
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        try:
            del self.toon
        except:
            print 'ColorShop: toon not found'

        self.hideButtons()

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        guiRArrowDown = self.gui.find('**/CrtATn_R_Arrow_DN')
        guiRArrowRollover = self.gui.find('**/CrtATn_R_Arrow_RLVR')
        guiRArrowUp = self.gui.find('**/CrtATn_R_Arrow_UP')
        self.headLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-1,
                                                                                                                                                                              1,
                                                                                                                                                                              1), text=TTLocalizer.ColorShopHead, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                               0), text_fg=(0.8,
                                                                                                                                                                                                                                                            0.1,
                                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                                            1), pos=(-0.9,
                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                     0.3), command=self.__swapHeadColor, extraArgs=[-1])
        self.headRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopHead, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                              0), text_fg=(0.8,
                                                                                                                                                                                                                                           0.1,
                                                                                                                                                                                                                                           0,
                                                                                                                                                                                                                                           1), pos=(0,
                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                    0.3), command=self.__swapHeadColor, extraArgs=[
         1])
        self.armLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-1,
                                                                                                                                                                             1,
                                                                                                                                                                             1), text=TTLocalizer.ColorShopBody, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                              0), text_fg=(0.8,
                                                                                                                                                                                                                                                           0.1,
                                                                                                                                                                                                                                                           0,
                                                                                                                                                                                                                                                           1), pos=(-0.9,
                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                    -0.1), command=self.__swapArmColor, extraArgs=[-1])
        self.armRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopBody, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                             0), text_fg=(0.8,
                                                                                                                                                                                                                                          0.1,
                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                          1), pos=(0,
                                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                                   -0.1), command=self.__swapArmColor, extraArgs=[
         1])
        self.allLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-1,
                                                                                                                                                                             1,
                                                                                                                                                                             1), text=TTLocalizer.ColorShopToonRetro, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                                   0), text_fg=(0.8,
                                                                                                                                                                                                                                                                0.1,
                                                                                                                                                                                                                                                                0,
                                                                                                                                                                                                                                                                1), pos=(-0.9,
                                                                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                                                                         -0.1), command=self.__swapAllColor, extraArgs=[-1])
        self.allRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopToonRetro, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                                  0), text_fg=(0.8,
                                                                                                                                                                                                                                               0.1,
                                                                                                                                                                                                                                               0,
                                                                                                                                                                                                                                               1), pos=(0,
                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                        -0.1), command=self.__swapAllColor, extraArgs=[
         1])
        self.legLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-1,
                                                                                                                                                                             1,
                                                                                                                                                                             1), text=TTLocalizer.ColorShopLegs, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                              0), text_fg=(0.8,
                                                                                                                                                                                                                                                           0.1,
                                                                                                                                                                                                                                                           0,
                                                                                                                                                                                                                                                           1), pos=(-0.9,
                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                    -0.5), command=self.__swapLegColor, extraArgs=[
         -1])
        self.legRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.ColorShopLegs, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                             0), text_fg=(0.8,
                                                                                                                                                                                                                                          0.1,
                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                          1), pos=(0,
                                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                                   -0.5), command=self.__swapLegColor, extraArgs=[1])
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.toggleAllButton = DirectButton(parent=aspect2d, relief=None, image=(
         guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(0.8,
                                                                                                                            1.1,
                                                                                                                            1.1), pos=(-0.1,
                                                                                                                                       0,
                                                                                                                                       0.55), text=TTLocalizer.ColorShopPartsRetro, text_scale=0.06, text_pos=(0.0,
                                                                                                                                                                                                               -0.02), command=self.__toggleAllColor)
        guiButton.removeNode()
        self.headLButton.hide()
        self.headRButton.hide()
        self.armLButton.hide()
        self.armRButton.hide()
        self.legLButton.hide()
        self.legRButton.hide()
        self.allLButton.hide()
        self.allRButton.hide()
        self.toggleAllButton.hide()
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.headLButton.destroy()
        self.headRButton.destroy()
        self.armLButton.destroy()
        self.armRButton.destroy()
        self.legLButton.destroy()
        self.legRButton.destroy()
        self.allLButton.destroy()
        self.allRButton.destroy()
        self.toggleAllButton.destroy()
        del self.headLButton
        del self.headRButton
        del self.armLButton
        del self.armRButton
        del self.legLButton
        del self.legRButton
        del self.allLButton
        del self.allRButton
        del self.toggleAllButton

    def __toggleAllColor(self):
        if self.colorAll:
            self.colorAll = 0
            self.toggleAllButton['text'] = TTLocalizer.ColorShopAllRetro
        else:
            self.colorAll = 1
            self.toggleAllButton['text'] = TTLocalizer.ColorShopPartsRetro
            self.legChoice = self.headChoice
            self.armChoice = self.headChoice
            self.__swapAllColor(0)
        self.showButtons()

    def __swapAllColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        choice = (self.headChoice + offset) % length
        self.__updateScrollButtons(choice, length, self.allLButton, self.allRButton)
        self.__swapHeadColor(offset)
        self.__swapArmColor(offset)
        self.__swapLegColor(offset)

    def __swapHeadColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateScrollButtons(self.headChoice, length, self.headLButton, self.headRButton)
        newColor = colorList[self.headChoice]
        self.dna.headColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapArmColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.armChoice = (self.armChoice + offset) % length
        self.__updateScrollButtons(self.armChoice, length, self.armLButton, self.armRButton)
        newColor = colorList[self.armChoice]
        self.dna.armColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapLegColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.legChoice = (self.legChoice + offset) % length
        self.__updateScrollButtons(self.legChoice, length, self.legLButton, self.legRButton)
        newColor = colorList[self.legChoice]
        self.dna.legColor = newColor
        self.toon.swapToonColor(self.dna)

    def __updateScrollButtons(self, choice, length, lButton, rButton):
        if choice == (self.startColor - 1) % length:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice == self.startColor % length:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)