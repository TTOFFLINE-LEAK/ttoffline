import random
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.fsm import StateData
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
from panda3d.core import *
import BodyShop, ColorShop, GenderShop, MakeClothesGUI, NameShop
from MakeAToonGlobals import *
from libotp.nametag import NametagGlobals
from libotp.nametag._constants import CFSpeech
from toontown.char import Char
from toontown.char import CharDNA
from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class MakeAToon(StateData.StateData):

    def __init__(self, parentFSM, avList, doneEvent, index, isPaid):
        self.isPaid = isPaid
        StateData.StateData.__init__(self, doneEvent)
        self.phase = 3
        self.names = ['', '', '', '']
        self.dnastring = None
        self.dna = None
        self.progressing = 0
        self.hostPosition = Point3(4.2, -1.9, 0)
        self.toonPosition = Point3(-1.5, -2.0, 0)
        self.hostHpr = Point3(160, 0, 0)
        self.toonHpr = Point3(200, 0, 0)
        self.leftTime = 1.6
        self.rightTime = 1
        self.slide = 0
        self.nameList = []
        self.warp = 0
        for av in avList:
            if av.position == index:
                self.warp = 1
                self.namelessPotAv = av
            self.nameList.append(av.name)

        self.fsm = ClassicFSM.ClassicFSM('MakeAToon', [
         State.State('Init', self.enterInit, self.exitInit, [
          'GenderShop',
          'NameShop']),
         State.State('GenderShop', self.enterGenderShop, self.exitGenderShop, [
          'BodyShop']),
         State.State('BodyShop', self.enterBodyShop, self.exitBodyShop, [
          'GenderShop',
          'ColorShop']),
         State.State('ColorShop', self.enterColorShop, self.exitColorShop, [
          'BodyShop',
          'ClothesShop']),
         State.State('ClothesShop', self.enterClothesShop, self.exitClothesShop, [
          'ColorShop',
          'NameShop']),
         State.State('NameShop', self.enterNameShop, self.exitNameShop, [
          'ClothesShop']),
         State.State('Done', self.enterDone, self.exitDone, [])], 'Init', 'Done')
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('createAvatar').addChild(self.fsm)
        self.gs = GenderShop.GenderShop('GenderShop-done')
        self.bs = BodyShop.BodyShop('BodyShop-done')
        self.cos = ColorShop.ColorShop('ColorShop-done')
        self.cls = MakeClothesGUI.MakeClothesGUI('ClothesShop-done')
        self.ns = NameShop.NameShop(self.fsm, 'NameShop-done', avList, index, self.isPaid)
        self.shop = GENDERSHOP
        self.shopsVisited = []
        if self.warp:
            self.shopsVisited = [GENDERSHOP,
             BODYSHOP,
             COLORSHOP,
             CLOTHESSHOP]
        self.music = None
        self.soundBack = None
        self.fsm.enterInitialState()
        return

    def getToon(self):
        return self.toon

    def enter(self):
        base.camLens.setMinFov(ToontownGlobals.MakeAToonCameraFovRetro / (4.0 / 3.0))
        base.playMusic(self.music, looping=1, volume=self.musicVolume)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.toon.reparentTo(render)
        self.toon.setPosHprScale(-1.5, -2.0, 0, 200, 0, 0, 1.2, 1.2, 1.2)
        self.toon.loop('neutral')
        self.room.reparentTo(render)
        camera.setPosHpr(0.75, -22, 5.35, 0, -7.12, 0)
        if self.warp:
            if self.toon.style.torso[1] == 's':
                self.toon.gender = 's'
                self.host = self.mickey
                self.minnie.reparentTo(hidden)
            else:
                self.toon.gender = 'd'
                self.host = self.minnie
                self.mickey.reparentTo(hidden)
            self.host.setPickable(0)
            self.host.reparentTo(render)
            self.host.loop('neutral')
            self.host.setPosHpr(4.9, -1.9, 0, 160, 0, 0)
            self.toon.reparentTo(render)
            self.toon.loop('neutral')
            self.toon.setPosHpr(-4.09, -2, 0, 200, 0, 0)
        else:
            self.mickey.reparentTo(render)
            self.mickey.loop('neutral')
            self.mickey.setPosHpr(4.2, -1.9, 0, 160, 0, 0)
            self.minnie.reparentTo(render)
            self.minnie.loop('neutral')
            self.minnie.setPosHpr(-2.7, -1.9, 0, 210, 0, 0)
        NametagGlobals.setMasterNametagsActive(1)
        self.guiTopBar.show()
        self.guiBottomBar.show()
        self.guiCancelButton.show()
        if self.warp:
            self.progressing = 0
            self.guiLastButton.hide()
            self.fsm.request('NameShop')
        else:
            self.fsm.request('GenderShop')

    def exit(self):
        base.camLens.setMinFov(ToontownGlobals.DefaultCameraFov / (4.0 / 3.0))
        self.guiTopBar.hide()
        self.guiBottomBar.hide()
        self.music.stop()
        self.fsm.request('Done')
        self.toon.stopBlink()
        self.toon.stopLookAroundNow()
        self.toon.reparentTo(hidden)
        self.room.reparentTo(hidden)
        self.mickey.reparentTo(hidden)
        self.mickey.stop()
        self.minnie.reparentTo(hidden)
        self.minnie.stop()
        NametagGlobals.setMasterNametagsActive(0)

    def load(self):
        gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        self.guiTopBar = DirectFrame(relief=None, image=gui.find('**/CrtATn_TopBar'), text=TTLocalizer.CreateYourToon, text_font=ToontownGlobals.getSignFont(), text_fg=(0.0,
                                                                                                                                                                         0.65,
                                                                                                                                                                         0.35,
                                                                                                                                                                         1), text_scale=0.03, text_pos=(0,
                                                                                                                                                                                                        -0.03), pos=(0,
                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                     0.86))
        self.guiTopBar.hide()
        self.guiBottomBar = DirectFrame(relief=None, image=gui.find('**/CrtATn_BtmBar'), image_scale=(
         base.getAspectRatio() - 4.0 / 3.0 % 1.25, 1, 1), pos=(0.01, 0, -0.86))
        self.accept('aspectRatioChanged', self.aspectRatioChanged)
        self.guiBottomBar.hide()
        self.guiCheckButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(
         gui.find('**/CrtAtoon_Btn1_UP'), gui.find('**/CrtAtoon_Btn1_DOWN'), gui.find('**/CrtAtoon_Btn1_RLLVR')), pos=(1.165,
                                                                                                                       0,
                                                                                                                       -0.018), command=self.__handleNext, text=(
         '', TTLocalizer.MakeAToonDone, TTLocalizer.MakeAToonDone), text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_pos=(0,
                                                                                                                                             -0.03), text_fg=(1,
                                                                                                                                                              1,
                                                                                                                                                              1,
                                                                                                                                                              1), text_shadow=(0,
                                                                                                                                                                               0,
                                                                                                                                                                               0,
                                                                                                                                                                               1))
        self.guiCheckButton.hide()
        self.guiCancelButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(
         gui.find('**/CrtAtoon_Btn2_UP'), gui.find('**/CrtAtoon_Btn2_DOWN'), gui.find('**/CrtAtoon_Btn2_RLLVR')), pos=(-1.179,
                                                                                                                       0,
                                                                                                                       -0.011), command=self.__handleCancel, text=(
         '', TTLocalizer.MakeAToonCancel, TTLocalizer.MakeAToonCancel), text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.MATnextButtonScale, text_pos=(0,
                                                                                                                                                                           -0.03), text_fg=(1,
                                                                                                                                                                                            1,
                                                                                                                                                                                            1,
                                                                                                                                                                                            1), text_shadow=(0,
                                                                                                                                                                                                             0,
                                                                                                                                                                                                             0,
                                                                                                                                                                                                             1))
        self.guiCancelButton.hide()
        self.guiNextButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(
         gui.find('**/CrtAtoon_Btn3_UP'), gui.find('**/CrtAtoon_Btn3_DN'), gui.find('**/CrtAtoon_Btn3_RLVR')), pos=(1.165,
                                                                                                                    0,
                                                                                                                    -0.018), command=self.__handleNext, text=(
         '', TTLocalizer.MakeAToonNext, TTLocalizer.MakeAToonNext), text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.MATnextButtonScale, text_pos=(0,
                                                                                                                                                                       -0.03), text_fg=(1,
                                                                                                                                                                                        1,
                                                                                                                                                                                        1,
                                                                                                                                                                                        1), text_shadow=(0,
                                                                                                                                                                                                         0,
                                                                                                                                                                                                         0,
                                                                                                                                                                                                         1))
        self.guiNextButton.hide()
        self.guiLastButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(
         gui.find('**/CrtAtoon_Btn3_UP'), gui.find('**/CrtAtoon_Btn3_DN'), gui.find('**/CrtAtoon_Btn3_RLVR')), image_scale=(-1.0,
                                                                                                                            1,
                                                                                                                            1), pos=(0.825,
                                                                                                                                     0,
                                                                                                                                     -0.018), command=self.__handleLast, text=(
         '', TTLocalizer.MakeAToonLast, TTLocalizer.MakeAToonLast), text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_pos=(0,
                                                                                                                                             -0.03), text_fg=(1,
                                                                                                                                                              1,
                                                                                                                                                              1,
                                                                                                                                                              1), text_shadow=(0,
                                                                                                                                                                               0,
                                                                                                                                                                               0,
                                                                                                                                                                               1))
        self.guiLastButton.hide()
        gui.removeNode()
        self.room = loader.loadModel('phase_3/models/gui/create_a_toon')
        self.roomWalls = self.room.find('**/wall_floor')
        self.draftingTable = self.room.find('**/drafting_table')
        self.easel = self.room.find('**/easel')
        self.sewingMachine = self.room.find('**/sewing_machine')
        ee = DirectFrame(pos=(-1, 1, 1), frameSize=(-0.01, 0.01, -0.01, 0.01), frameColor=(0,
                                                                                           0,
                                                                                           0,
                                                                                           0.05), state='normal')
        ee.bind(DGG.B1PRESS, lambda x, ee=ee: self.toggleSlide())
        self.eee = ee
        self.stool = self.room.find('**/stool')
        self.stool.hide()
        self.draftingTable.hide()
        self.easel.hide()
        self.sewingMachine.hide()
        if not self.warp:
            self.dna = ToonDNA.ToonDNA()
            animalIndicesToUse = ToonDNA.toonHeadAnimalIndices[0:8]
            animal = random.choice(animalIndicesToUse)
            head = ToonDNA.toonHeadTypesMAT[animal]
            torso = random.choice(ToonDNA.toonTorsoTypes[-3:])
            leg = random.choice(ToonDNA.toonLegTypes)
            self.dna.newToon((head, torso, leg, 'm'))
        else:
            self.dna = ToonDNA.ToonDNA()
            self.dna.makeFromNetString(self.namelessPotAv.dna)
        self.toon = Toon.Toon()
        self.toon.setDNA(self.dna)
        self.toon.useLOD(1000)
        self.toon.setNameVisible(0)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.mickey = Char.Char()
        mickeyDNA = CharDNA.CharDNA()
        mickeyDNA.newChar('mk')
        self.mickey.setDNA(mickeyDNA)
        self.mickey.addActive()
        self.mickey.startEarTask()
        self.mickey.setNametagScale(0.8)
        self.mickey.hideName()
        self.mickey.setPickable(1)
        self.mickey.nametag.getNametag3d().setChatWordwrap(8)
        self.minnie = Char.Char()
        minnieDNA = CharDNA.CharDNA()
        minnieDNA.newChar('mn')
        self.minnie.setDNA(minnieDNA)
        self.minnie.addActive()
        self.minnie.startEarTask()
        self.minnie.setNametagScale(0.8)
        self.minnie.hideName()
        self.minnie.setPickable(1)
        self.minnie.nametag.getNametag3d().setChatWordwrap(8)
        self.gs.load()
        self.bs.load()
        self.cos.load()
        self.cls.load()
        self.ns.load()
        self.music = base.loader.loadMusic('phase_3/audio/bgm/create_a_toon.ogg')
        self.musicVolume = base.config.GetFloat('makeatoon-music-volume', 0.5)
        print self.musicVolume
        self.soundBack = base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_back.ogg')
        if base.config.GetString('language', 'english') == 'japanese':
            self.mickeyDialogueArray = [base.loader.loadSfx('phase_3/audio/dial/CC_mickey_create01.ogg'),
             base.loader.loadSfx('phase_3/audio/dial/CC_mickey_create02.ogg'),
             base.loader.loadSfx('phase_3/audio/dial/CC_mickey_create03.ogg')]
        else:
            self.mickeyDialogueArray = [
             None,
             None,
             None]
        if base.config.GetString('language', 'english') == 'japanese':
            self.minnieDialogueArray = [base.loader.loadSfx('phase_3/audio/dial/CC_minnie_create01.ogg'),
             base.loader.loadSfx('phase_3/audio/dial/CC_minnie_create02.ogg'),
             base.loader.loadSfx('phase_3/audio/dial/CC_minnie_create03.ogg')]
        else:
            self.minnieDialogueArray = [
             None,
             None,
             None]
        return

    def unload(self):
        self.exit()
        del self.stool
        del self.draftingTable
        del self.easel
        del self.sewingMachine
        self.room.removeNode()
        del self.room
        self.toon.stopBlink()
        self.toon.stopLookAroundNow()
        self.gs.unload()
        if hasattr(self, 'exitGenderTrack'):
            self.exitGenderTrack.pause()
            del self.exitGenderTrack
        self.bs.unload()
        self.cos.unload()
        self.cls.unload()
        self.ns.unload()
        if hasattr(self, 'hostTrack'):
            self.hostTrack.pause()
            del self.hostTrack
        del self.gs
        del self.bs
        del self.cos
        del self.cls
        del self.ns
        self.guiTopBar.destroy()
        del self.guiTopBar
        self.guiBottomBar.destroy()
        del self.guiBottomBar
        del self.guiCancelButton
        del self.guiCheckButton
        self.eee.destroy()
        del self.eee
        del self.guiNextButton
        del self.guiLastButton
        del self.names
        del self.dnastring
        del self.nameList
        del self.music
        del self.soundBack
        del self.dna
        self.toon.delete()
        del self.toon
        self.mickey.removeActive()
        self.mickey.stopEarTask()
        self.mickey.delete()
        del self.mickey
        self.minnie.removeActive()
        self.minnie.stopEarTask()
        self.minnie.delete()
        del self.minnie
        self.parentFSM.getStateNamed('createAvatar').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        loader.unloadModel('phase_3/models/gui/create_a_toon_gui')
        loader.unloadModel('phase_3/models/gui/create_a_toon')
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def getDNA(self):
        return self.dnastring

    def __handleBodyShop(self):
        self.fsm.request('BodyShop')

    def __handleClothesShop(self):
        self.fsm.request('ClothesShop')

    def __handleColorShop(self):
        self.fsm.request('ColorShop')

    def __handleNameShop(self):
        self.fsm.request('NameShop')

    def __handleCancel(self):
        self.doneStatus = 'cancel'
        self.shopsVisited = []
        base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))

    def toggleSlide(self):
        self.slide = 1 - self.slide

    def goToNextShop(self):
        self.progressing = 1
        if self.shop == GENDERSHOP:
            self.fsm.request('BodyShop')
        else:
            if self.shop == BODYSHOP:
                self.fsm.request('ColorShop')
            else:
                if self.shop == COLORSHOP:
                    self.fsm.request('ClothesShop')
                else:
                    self.fsm.request('NameShop')

    def goToLastShop(self):
        self.progressing = 0
        if self.shop == BODYSHOP:
            self.fsm.request('GenderShop')
        else:
            if self.shop == COLORSHOP:
                self.fsm.request('BodyShop')
            else:
                if self.shop == CLOTHESSHOP:
                    self.fsm.request('ColorShop')
                else:
                    self.fsm.request('ClothesShop')

    def hostSez(self, stringList, dialogue=None):
        self.host.setChatAbsolute(random.choice(stringList), CFSpeech, dialogue)

    def charSez(self, char, statement, dialogue=None):
        char.setChatAbsolute(statement, CFSpeech, dialogue)

    def enterInit(self):
        pass

    def exitInit(self):
        pass

    def charRunFromLeft(self, char, newpos, newhpr, timelimit=1.6, comm=None, eA=[]):
        myInterval = Sequence()
        myInterval.append(Func(self.host.clearChat))
        myInterval.append(Func(char.setPosHpr, -12 + newpos[0], -4.5, 0, 270, 0, 0))
        if not self.slide:
            myInterval.append(Func(char.loop, 'run'))
        myInterval.append(LerpPosInterval(char, duration=timelimit, pos=newpos))
        myInterval.append(LerpHprInterval(char, duration=0.3, hpr=newhpr))
        myInterval.append(Func(char.loop, 'neutral'))
        if comm:
            myInterval.append(Func(comm, *eA))
        return myInterval

    def charRunToLeft(self, char, timelimit=1.6, comm=None, eA=[]):
        myInterval = Sequence()
        if not self.slide:
            myInterval.append(Func(char.loop, 'run'))
        myInterval.append(LerpHprInterval(char, duration=0.3, hpr=Point3(80, 0, 0)))
        myInterval.append(Func(self.host.clearChat))
        myInterval.append(LerpPosInterval(char, duration=timelimit, pos=Point3(-12 + char.getPos()[0], -4.5, 0)))
        myInterval.append(Func(char.loop, 'neutral'))
        if comm:
            myInterval.append(Func(comm, *eA))
        return myInterval

    def charRunFromRight(self, char, newpos, newhpr, timelimit=1, comm=None, eA=[]):
        myInterval = Sequence()
        myInterval.append(Func(self.host.clearChat))
        myInterval.append(Func(char.setPosHpr, 9.5 + newpos[0], -4.5, 0, 80, 0, 0))
        if not self.slide:
            myInterval.append(Func(char.loop, 'run'))
        myInterval.append(LerpPosInterval(char, duration=timelimit, pos=newpos))
        myInterval.append(LerpHprInterval(char, duration=0.3, hpr=newhpr))
        myInterval.append(Func(char.loop, 'neutral'))
        if comm:
            myInterval.append(Func(comm, *eA))
        return myInterval

    def charRunToRight(self, char, timelimit=1, comm=None, eA=[]):
        myInterval = Sequence()
        if not self.slide:
            myInterval.append(Func(char.loop, 'run'))
        myInterval.append(LerpHprInterval(char, duration=0.3, hpr=Point3(270, 0, 0)))
        myInterval.append(Func(self.host.clearChat))
        myInterval.append(LerpPosInterval(char, duration=timelimit, pos=Point3(char.getPos()[0] + 9.5, -4.5, 0)))
        myInterval.append(Func(char.loop, 'neutral'))
        if comm:
            myInterval.append(Func(comm, *eA))
        return myInterval

    def genderShopOpening(self, task):
        self.host = self.minnie
        self.hostSez([
         TTLocalizer.GenderShopQuestionMinnie], self.minnieDialogueArray[0])
        if base.config.GetString('language', 'english') == 'japanese':
            taskMgr.doMethodLater(4.0, self.genderShopOpening2, 'genderShopOpeningTask2')
        else:
            self.genderShopOpening2()
        return Task.done

    def genderShopOpening2(self, task=None):
        self.host = self.mickey
        self.hostSez([
         TTLocalizer.GenderShopQuestionMickey], self.mickeyDialogueArray[0])
        return Task.done

    def enterGenderShop(self):
        self.toon.hide()
        self.roomWalls.setColorScale(0.74, 0.54, 0.4, 1)
        self.mickey.reparentTo(render)
        self.mickey.loop('neutral')
        self.mickey.setPosHpr(4.2, -1.9, 0, 160, 0, 0)
        self.minnie.setPickable(1)
        self.mickey.setPickable(1)
        self.minnie.reparentTo(render)
        self.minnie.loop('neutral')
        self.minnie.setPosHpr(-2.7, -1.9, 0, 210, 0, 0)
        self.shop = GENDERSHOP
        self.guiTopBar['text'] = TTLocalizer.CreateYourToonTitleRetro
        self.guiTopBar['text_fg'] = (1, 0.9, 0, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterGenderShop
        base.transitions.fadeIn()
        self.accept('GenderShop-done', self.__handleGenderShopDone)
        self.accept('clickedNametag', self.__handleBodyClick)
        self.gs.enter()
        taskMgr.doMethodLater(0.8, self.genderShopOpening, 'genderShopOpeningTask')

    def exitGenderShop(self):
        self.gs.exit()
        self.ignore('GenderShop-done')
        taskMgr.remove('genderShopOpeningTask')
        taskMgr.remove('genderShopOpeningTask2')
        if self.gs.gender == 'm':
            self.minnie.reparentTo(hidden)
            self.minnie.stop()
        else:
            self.mickey.reparentTo(hidden)
            self.mickey.stop()

    def __handleGenderShopDone(self):
        taskMgr.remove('genderShopOpeningTask2')
        self.minnie.setPickable(0)
        self.mickey.setPickable(0)
        self.toon.style.gender = self.gs.gender
        gendershopInterval = Sequence()
        gendershopInterval.append(Wait(1.0))
        if self.toon.style.gender == 'm':
            self.timeToGetOff = 1
            self.minnie.clearChat()
            gendershopInterval.append(Func(self.charSez, self.minnie, TTLocalizer.GenderShopSeeYou, self.minnieDialogueArray[2]))
            self.host = self.mickey
            self.hostSez([
             TTLocalizer.GenderShopFollow], self.mickeyDialogueArray[1])
        else:
            self.timeToGetOff = self.leftTime
            self.mickey.clearChat()
            gendershopInterval.append(Func(self.charSez, self.mickey, TTLocalizer.GenderShopSeeYou, self.mickeyDialogueArray[2]))
            self.host = self.minnie
            self.hostSez([
             TTLocalizer.GenderShopFollow], self.minnieDialogueArray[1])
        self.toon.setupEyelashes(self.toon.style)
        gendershopInterval.append(Func(self.host.clearChat))
        gendershopInterval.append(self.charRunToRight(char=self.host, timelimit=self.timeToGetOff, comm=self.goToNextShop))
        gendershopInterval.append(Func(self.mickey.clearChat))
        gendershopInterval.append(Func(self.minnie.clearChat))
        self.exitGenderTrack = gendershopInterval
        self.exitGenderTrack.start()

    def bodyShopOpening(self):
        self.hostSez([
         TTLocalizer.CreateYourToon])
        self.bs.showButtons()
        self.guiNextButton.show()
        self.guiLastButton.show()

    def enterBodyShop(self):
        self.toon.show()
        self.roomWalls.setColorScale(0.9, 0.75, 0.45, 1)
        self.shop = BODYSHOP
        self.guiTopBar['text'] = TTLocalizer.CreateYourToonTitleRetro
        self.guiTopBar['text_fg'] = (0.0, 0.65, 0.35, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterBodyShop
        self.accept('BodyShop-done', self.__handleBodyShopDone)
        self.draftingTable.show()
        self.bs.enter(self.toon, self.shopsVisited)
        if BODYSHOP not in self.shopsVisited:
            self.shopsVisited.append(BODYSHOP)
        if self.progressing:
            self.hostTrack = self.charRunFromLeft(char=self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.bodyShopOpening)
            self.hostTrack.start()
        else:
            self.hostTrack = Parallel(self.charRunFromRight(char=self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.bodyShopOpening), self.charRunFromRight(char=self.toon, newpos=self.toonPosition, newhpr=self.toonHpr))
            self.hostTrack.start()
        taskMgr.doMethodLater(16.0, self.bodyShopDialogTask, 'bodyShopDialogTask')

    def bodyShopDialogTask(self, task):
        self.hostSez([
         TTLocalizer.MakeAToonClickForNextScreen])
        return Task.done

    def exitBodyShop(self):
        self.bs.exit()
        self.host.clearChat()
        self.ignore('BodyShop-done')
        taskMgr.remove('bodyShopDialogTask')
        taskMgr.remove('bodyShopOpeningTask')
        self.draftingTable.hide()

    def __handleBodyShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.bs.doneStatus == 'next':
            self.bs.hideButtons()
            self.hostTrack = Parallel(self.charRunToRight(char=self.host, comm=self.goToNextShop), self.charRunToRight(char=self.toon))
            self.hostTrack.start()
        else:
            self.bs.hideButtons()
            self.hostTrack = self.charRunToLeft(char=self.host, comm=self.goToLastShop)
            self.hostTrack.start()

    def colorShopOpening(self):
        self.hostSez([
         TTLocalizer.PaintYourToon])
        self.cos.showButtons()
        self.guiNextButton.show()
        self.guiLastButton.show()

    def enterColorShop(self):
        self.shop = COLORSHOP
        self.roomWalls.setColorScale(0.61, 0.7, 0.45, 1)
        self.guiTopBar['text'] = TTLocalizer.PaintYourToonTitleRetro
        self.guiTopBar['text_fg'] = (0.15, 0.4, 0.8, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterColorShop
        self.accept('ColorShop-done', self.__handleColorShopDone)
        self.easel.show()
        if self.progressing:
            self.hostTrack = Parallel(self.charRunFromLeft(self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.colorShopOpening), self.charRunFromLeft(self.toon, newpos=self.toonPosition, newhpr=self.toonHpr))
            self.hostTrack.start()
        else:
            self.hostTrack = Parallel(self.charRunFromRight(self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.colorShopOpening), self.charRunFromRight(self.toon, newpos=self.toonPosition, newhpr=self.toonHpr))
            self.hostTrack.start()
        self.cos.enter(self.toon, self.shopsVisited)
        if COLORSHOP not in self.shopsVisited:
            self.shopsVisited.append(COLORSHOP)
        taskMgr.doMethodLater(8.0, self.colorShopDialogTask, 'colorShopDialogTask')

    def colorShopDialogTask(self, task):
        self.hostSez([
         TTLocalizer.MakeAToonYouCanGoBack])
        return Task.done

    def exitColorShop(self):
        self.cos.exit()
        self.host.clearChat()
        self.ignore('ColorShop-done')
        taskMgr.remove('colorShopOpeningTask')
        taskMgr.remove('colorShopDialogTask')
        self.easel.hide()

    def __handleColorShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.cos.doneStatus == 'next':
            self.cos.hideButtons()
            self.hostTrack = Parallel(self.charRunToRight(char=self.host, comm=self.goToNextShop), self.charRunToRight(char=self.toon))
            self.hostTrack.start()
        else:
            self.cos.hideButtons()
            self.hostTrack = Parallel(self.charRunToLeft(char=self.host, comm=self.goToLastShop), self.charRunToLeft(char=self.toon))
            self.hostTrack.start()

    def clothesShopOpening(self):
        self.hostSez([
         TTLocalizer.PickClothes])
        self.guiNextButton.show()
        self.guiLastButton.show()
        self.cls.showButtons()

    def enterClothesShop(self):
        self.shop = CLOTHESSHOP
        self.roomWalls.setColorScale(0.93, 0.64, 0.46, 1)
        self.guiTopBar['text'] = TTLocalizer.PickClothesTitleRetro
        self.guiTopBar['text_fg'] = (1, 0.9, 0, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterClothesShop
        self.accept('ClothesShop-done', self.__handleClothesShopDone)
        self.sewingMachine.show()
        self.toon.setScale(1.2, 1.2, 1.2)
        self.host.setScale(1, 1, 1)
        if self.progressing:
            self.hostTrack = Parallel(self.charRunFromLeft(self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.clothesShopOpening), self.charRunFromLeft(self.toon, newpos=self.toonPosition, newhpr=self.toonHpr))
            self.hostTrack.start()
        else:
            self.hostTrack = Parallel(self.charRunFromRight(self.host, newpos=self.hostPosition, newhpr=self.hostHpr, comm=self.clothesShopOpening), self.charRunFromRight(self.toon, newpos=self.toonPosition, newhpr=self.toonHpr))
            self.hostTrack.start()
        self.cls.enter(self.toon)
        if CLOTHESSHOP not in self.shopsVisited:
            self.shopsVisited.append(CLOTHESSHOP)

    def exitClothesShop(self):
        self.cls.exit()
        taskMgr.remove('clothesShopOpeningTask')
        self.host.clearChat()
        self.ignore('ClothesShop-done')
        self.sewingMachine.hide()

    def __handleClothesShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.cls.doneStatus == 'next':
            self.cls.hideButtons()
            self.hostTrack = Parallel(self.charRunToRight(char=self.host), self.charRunToRight(char=self.toon, comm=self.goToNextShop))
            self.hostTrack.start()
        else:
            self.cls.hideButtons()
            self.hostTrack = Parallel(self.charRunToLeft(char=self.host, comm=self.goToLastShop), self.charRunToLeft(char=self.toon))
            self.hostTrack.start()

    def nameShopOpening(self, task):
        self.guiCheckButton.show()
        self.guiLastButton.show()
        if self.warp:
            self.guiLastButton.hide()
        if NAMESHOP not in self.shopsVisited:
            self.shopsVisited.append(NAMESHOP)
            self.hostSez([
             TTLocalizer.MakeAFunnyName])
        else:
            self.hostSez([
             TTLocalizer.MakeAToonLastStep,
             TTLocalizer.PickANameYouLike])
        return Task.done

    def enterNameShop(self):
        self.shop = NAMESHOP
        self.roomWalls.setColorScale(0.9, 0.75, 0.45, 1)
        self.guiTopBar['text'] = TTLocalizer.NameToonTitleRetro
        self.guiTopBar['text_fg'] = (0.0, 0.65, 0.35, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterNameShop
        self.accept('NameShop-done', self.__handleNameShopDone)
        self.accept('NameShop-mickeyChange', self.__changeHost)
        self.host.setScale(0.9, 0.9, 0.9)
        if self.progressing:
            self.hostTrack = Parallel(self.charRunFromLeft(self.host, newpos=Point3(4.9, -1.9, 0), newhpr=self.hostHpr, comm=self.ns.enter, eA=[
             self.toon,
             self.nameList,
             self.warp]), self.charRunFromLeft(self.toon, newpos=Point3(-4.09, -2.0, 0), newhpr=self.toonHpr))
            self.hostTrack.start()
            waittime = self.leftTime
        else:
            self.ns.enter(self.toon, self.nameList, self.warp)
            waittime = 0.2
        taskMgr.doMethodLater(waittime, self.nameShopOpening, 'nameShopOpeningTask')

    def exitNameShop(self):
        self.ns.exit()
        self.host.clearChat()
        self.ignore('NameShop-done')
        self.ignore('NameShop-mickeyChange')
        taskMgr.remove('nameShopOpeningTask')

    def rejectName(self):
        self.ns.rejectName(TTLocalizer.RejectNameText)

    def __handleBodyClick(self, clickedAvatar):
        if clickedAvatar == self.mickey:
            self.gs.setGender(-1)
        else:
            self.gs.setGender(1)

    def __changeHost(self, newText):
        self.hostSez(newText)

    def __handleNameShopDone(self):
        self.guiLastButton.hide()
        self.guiCheckButton.hide()
        if self.ns.getDoneStatus() == 'last':
            self.ns.hideAll()
            self.hostTrack = Parallel(self.charRunToLeft(char=self.host, comm=self.goToLastShop), self.charRunToLeft(char=self.toon))
            self.hostTrack.start()
        else:
            if self.ns.getDoneStatus() == 'paynow':
                self.doneStatus = 'paynow'
                base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))
            else:
                self.doneStatus = 'created'
                base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))

    def __handleNext(self):
        messenger.send('next')

    def __handleLast(self):
        messenger.send('last')

    def enterDone(self):
        pass

    def exitDone(self):
        pass

    def aspectRatioChanged(self):
        self.guiBottomBar['image_scale'] = (
         base.getAspectRatio() - 4.0 / 3.0 % 1.25, 1, 1)