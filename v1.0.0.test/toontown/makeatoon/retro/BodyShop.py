from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import *
from MakeAToonGlobals import *
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer

class BodyShop(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('BodyShop')

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.torsoChoice = 0
        self.legChoice = 0
        self.headChoice = 0
        return

    def enter(self, toon, shopsVisited=[]):
        base.disableMouse()
        self.toon = toon
        self.dna = self.toon.getStyle()
        gender = self.toon.style.getGender()
        if BODYSHOP not in shopsVisited:
            self.headLButton['state'] = DGG.DISABLED
            self.torsoLButton['state'] = DGG.DISABLED
            self.legLButton['state'] = DGG.DISABLED
            self.headStart = ToonDNA.toonHeadTypesMAT.index(self.dna.head)
            self.torsoStart = ToonDNA.toonTorsoTypes.index(self.dna.torso)
            self.legStart = ToonDNA.toonLegTypes.index(self.dna.legs)
            self.headChoice = self.headStart
            self.torsoChoice = self.torsoStart % 3
            self.legChoice = self.legStart
        else:
            self.headChoice = ToonDNA.toonHeadTypesMAT.index(self.dna.head)
            self.torsoChoice = ToonDNA.toonTorsoTypes.index(self.dna.torso) % 3
            self.legChoice = ToonDNA.toonLegTypes.index(self.dna.legs)
        if CLOTHESSHOP in shopsVisited:
            self.clothesPicked = 1
        else:
            self.clothesPicked = 0
        if len(self.dna.torso) != 1:
            if gender == 'm' or ToonDNA.GirlBottoms[self.dna.botTex][1] == ToonDNA.SHORTS:
                torsoStyle = 's'
            else:
                torsoStyle = 'd'
            self.__swapTorso(0)
            self.__swapHead(0)
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)

    def showButtons(self):
        self.headLButton.show()
        self.headRButton.show()
        self.torsoLButton.show()
        self.torsoRButton.show()
        self.legLButton.show()
        self.legRButton.show()

    def hideButtons(self):
        self.headLButton.hide()
        self.headRButton.hide()
        self.torsoLButton.hide()
        self.torsoRButton.hide()
        self.legLButton.hide()
        self.legRButton.hide()

    def exit(self):
        try:
            del self.toon
        except:
            self.notify.warning('BodyShop: toon not found')

        self.hideButtons()
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        guiRArrowDown = self.gui.find('**/CrtATn_R_Arrow_DN')
        guiRArrowRollover = self.gui.find('**/CrtATn_R_Arrow_RLVR')
        guiRArrowUp = self.gui.find('**/CrtATn_R_Arrow_UP')
        self.headLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image_scale=(-1,
                                                                                                                                      1,
                                                                                                                                      1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), pos=(-0.9,
                                                                                                                                                                                       0,
                                                                                                                                                                                       0.3), text=TTLocalizer.BodyShopHead, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                                         0), text_fg=(0.8,
                                                                                                                                                                                                                                                                      0.1,
                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                      1), command=self.__swapHead, extraArgs=[-1])
        self.headRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.BodyShopHead, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                             0), text_fg=(0.8,
                                                                                                                                                                                                                                          0.1,
                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                          1), pos=(0,
                                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                                   0.3), command=self.__swapHead, extraArgs=[1])
        self.torsoLButton = DirectButton(relief=None, image=(
         guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image_scale=(-1,
                                                                                   1,
                                                                                   1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.BodyShopBody, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                           0), text_fg=(0.8,
                                                                                                                                                                                                        0.1,
                                                                                                                                                                                                        0,
                                                                                                                                                                                                        1), pos=(-0.9,
                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                 -0.1), command=self.__swapTorso, extraArgs=[-1])
        self.torsoRButton = DirectButton(relief=None, image=(
         guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.BodyShopBody, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                          0), text_fg=(0.8,
                                                                                                                                                                                       0.1,
                                                                                                                                                                                       0,
                                                                                                                                                                                       1), pos=(0,
                                                                                                                                                                                                0,
                                                                                                                                                                                                -0.1), command=self.__swapTorso, extraArgs=[
         1])
        self.legLButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image_scale=(-1,
                                                                                                                                     1,
                                                                                                                                     1), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.BodyShopLegs, text_scale=0.0625, text_pos=(0.025,
                                                                                                                                                                                                                                             0), text_fg=(0.8,
                                                                                                                                                                                                                                                          0.1,
                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                          1), pos=(-0.9,
                                                                                                                                                                                                                                                                   0,
                                                                                                                                                                                                                                                                   -0.5), command=self.__swapLegs, extraArgs=[
         -1])
        self.legRButton = DirectButton(relief=None, image=(guiRArrowUp, guiRArrowDown, guiRArrowRollover, guiRArrowUp), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), text=TTLocalizer.BodyShopLegs, text_scale=0.0625, text_pos=(-0.025,
                                                                                                                                                                                                                            0), text_fg=(0.8,
                                                                                                                                                                                                                                         0.1,
                                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                                         1), pos=(0,
                                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                                  -0.5), command=self.__swapLegs, extraArgs=[1])
        self.headLButton.hide()
        self.headRButton.hide()
        self.torsoLButton.hide()
        self.torsoRButton.hide()
        self.legLButton.hide()
        self.legRButton.hide()
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.headLButton.destroy()
        self.headRButton.destroy()
        self.torsoLButton.destroy()
        self.torsoRButton.destroy()
        self.legLButton.destroy()
        self.legRButton.destroy()
        del self.headLButton
        del self.headRButton
        del self.torsoLButton
        del self.torsoRButton
        del self.legLButton
        del self.legRButton

    def __swapTorso(self, offset):
        gender = self.toon.style.getGender()
        if not self.clothesPicked:
            length = len(ToonDNA.toonTorsoTypes[6:])
            torsoOffset = 6
        elif gender == 'm':
            length = len(ToonDNA.toonTorsoTypes[:3])
            torsoOffset = 0
            if self.dna.armColor not in ToonDNA.defaultBoyColorList:
                self.dna.armColor = ToonDNA.defaultBoyColorList[0]
            if self.dna.legColor not in ToonDNA.defaultBoyColorList:
                self.dna.legColor = ToonDNA.defaultBoyColorList[0]
            if self.dna.headColor not in ToonDNA.defaultBoyColorList:
                self.dna.headColor = ToonDNA.defaultBoyColorList[0]
            if self.toon.style.topTex not in ToonDNA.MakeAToonBoyShirts:
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in ToonDNA.MakeAToonBoyBottoms:
                botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON)
                self.toon.style.botTex = botTex
                self.toon.style.botTexColor = botTexColor
        else:
            length = len(ToonDNA.toonTorsoTypes[3:6])
            if self.toon.style.torso[1] == 'd':
                torsoOffset = 3
            else:
                torsoOffset = 0
            if self.dna.armColor not in ToonDNA.defaultGirlColorList:
                self.dna.armColor = ToonDNA.defaultGirlColorList[0]
            if self.dna.legColor not in ToonDNA.defaultGirlColorList:
                self.dna.legColor = ToonDNA.defaultGirlColorList[0]
            if self.dna.headColor not in ToonDNA.defaultGirlColorList:
                self.dna.headColor = ToonDNA.defaultGirlColorList[0]
            if self.toon.style.topTex not in ToonDNA.MakeAToonGirlShirts:
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in ToonDNA.MakeAToonGirlBottoms:
                if self.toon.style.torso[1] == 'd':
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SKIRT)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 3
                else:
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SHORTS)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 0
        self.torsoChoice = (self.torsoChoice + offset) % length
        self.__updateScrollButtons(self.torsoChoice, length, self.torsoStart, self.torsoLButton, self.torsoRButton)
        torso = ToonDNA.toonTorsoTypes[(torsoOffset + self.torsoChoice)]
        self.dna.torso = torso
        self.toon.swapToonTorso(torso)
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)

    def __swapLegs(self, offset):
        length = len(ToonDNA.toonLegTypes)
        self.legChoice = (self.legChoice + offset) % length
        self.notify.debug('self.legChoice=%d, length=%d, self.legStart=%d' % (self.legChoice, length, self.legStart))
        self.__updateScrollButtons(self.legChoice, length, self.legStart, self.legLButton, self.legRButton)
        newLeg = ToonDNA.toonLegTypes[self.legChoice]
        self.dna.legs = newLeg
        self.toon.swapToonLegs(newLeg)
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)

    def __swapHead(self, offset):
        length = len(ToonDNA.toonHeadTypesMAT)
        if not base.config.GetBool('allow-pig', 1):
            length -= 4
        self.headChoice = (self.headChoice + offset) % length
        self.__updateScrollButtons(self.headChoice, length, self.headStart, self.headLButton, self.headRButton)
        newHead = ToonDNA.toonHeadTypesMAT[self.headChoice]
        self.dna.head = newHead
        self.toon.swapToonHead(newHead)
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)

    def __updateScrollButtons(self, choice, length, start, lButton, rButton):
        if choice == (start - 1) % length:
            rButton['state'] = DGG.DISABLED
        elif choice == (start - 2) % length:
            rButton['state'] = DGG.NORMAL
        if choice == start % length:
            lButton['state'] = DGG.DISABLED
        elif choice == (start + 1) % length:
            lButton['state'] = DGG.NORMAL
        if lButton['state'] == DGG.DISABLED and rButton['state'] == DGG.DISABLED:
            self.notify.info('Both buttons got disabled! Doing fallback code. choice%d, length=%d, start=%d, lButton=%s, rButton=%s' % (
             choice, length, start, lButton, rButton))
            if choice == start % length:
                lButton['state'] = DGG.DISABLED
                rButton['state'] = DGG.NORMAL
            elif choice == (start - 1) % length:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.DISABLED
            else:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)