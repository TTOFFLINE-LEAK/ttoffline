import string
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.PyDatagram import PyDatagram
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.fsm import StateData
from direct.gui.DirectGui import *
from direct.gui import OnscreenText
from otp.otpbase import PythonUtil
from direct.task import Task
from direct.task.TaskManagerGlobal import *
from otp.distributed import PotentialAvatar
from otp.namepanel import NameCheck
from toontown.makeatoon import NameGenerator
from toontown.toon import NPCToons
from toontown.toonbase.ToontownGlobals import *
from toontown.toontowngui import TTDialog
from toontown.toontowngui import TeaserPanel
from toontown.makeatoon.TTPickANamePattern import TTPickANamePattern
MAX_NAME_WIDTH = TTLocalizer.NSmaxNameWidthRetro
ServerDialogTimeout = 3.0

class NameShop(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('NameShop')

    def __init__(self, parentFSM, doneEvent, avList, index, isPaid):
        StateData.StateData.__init__(self, doneEvent)
        self.isPaid = isPaid
        self.avList = avList
        self.index = index
        self.shopsVisited = []
        self.avId = -1
        self.avExists = 0
        self.names = [
         '',
         '',
         '',
         '']
        self.toon = None
        self.boy = 0
        self.girl = 0
        self.allTitles = []
        self.allFirsts = []
        self.allPrefixes = []
        self.allSuffixes = []
        self.titleIndex = 0
        self.firstIndex = 0
        self.prefixIndex = 0
        self.suffixIndex = 0
        self.titleActive = 0
        self.firstActive = 0
        self.lastActive = 0
        self.quickFind = 0
        self.listsLoaded = 0
        self.addedGenderSpecific = 0
        self.chastise = 0
        self.nameIndices = [
         -1,
         -1,
         -1,
         -1]
        self.nameFlags = [
         1,
         1,
         1,
         0]
        self.dummyReturn = 2
        self.nameAction = 0
        self.pickANameGUIElements = []
        self.typeANameGUIElements = []
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.fsm = ClassicFSM.ClassicFSM('NameShop', [
         State.State('Init', self.enterInit, self.exitInit, [
          'PayState']),
         State.State('PayState', self.enterPayState, self.exitPayState, [
          'PickAName']),
         State.State('PickAName', self.enterPickANameState, self.exitPickANameState, [
          'TypeAName',
          'Done']),
         State.State('TypeAName', self.enterTypeANameState, self.exitTypeANameState, [
          'PickAName',
          'Approval',
          'Accepted',
          'Rejected']),
         State.State('Approval', self.enterApprovalState, self.exitApprovalState, ['PickAName', 'ApprovalAccepted']),
         State.State('ApprovalAccepted', self.enterApprovalAcceptedState, self.exitApprovalAcceptedState, ['Done']),
         State.State('Accepted', self.enterAcceptedState, self.exitAcceptedState, [
          'ApprovalAccepted',
          'Done']),
         State.State('Rejected', self.enterRejectedState, self.exitRejectedState, [
          'TypeAName']),
         State.State('Done', self.enterDone, self.exitDone, [
          'Init'])], 'Init', 'Done')
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('NameShop').addChild(self.fsm)
        self.nameGen = NameGenerator.NameGenerator()
        self.fsm.enterInitialState()
        self.requestingSkipTutorial = False
        return

    def makeLabel(self, te, index, others):
        alig = others[0]
        listName = others[1]
        if alig == TextNode.ARight:
            newpos = (0.44, 0, 0)
        elif alig == TextNode.ALeft:
            newpos = (0, 0, 0)
        else:
            newpos = (0.2, 0, 0)
        df = DirectFrame(state='normal', relief=None, text=te, text_scale=TTLocalizer.NSmakeLabel, text_pos=newpos, text_align=alig, textMayChange=0)
        df.bind(DGG.B1PRESS, lambda x, df=df: self.nameClickedOn(listName, index))
        return df

    def nameClickedOn(self, listType, index):
        if listType == 'title':
            self.titleIndex = index
        elif listType == 'first':
            self.firstIndex = index
        elif listType == 'prefix':
            self.prefixIndex = index
        else:
            self.suffixIndex = index
        self.updateLists()
        self.__listsChanged()

    def enter(self, toon, usedNames, warp):
        self.notify.debug('enter')
        self.newwarp = warp
        self.avExists = warp
        if self.avExists:
            for g in self.avList:
                if g.position == self.index:
                    self.avId = g.id

        if toon == None:
            return
        else:
            self.toon = toon
            if self.toon.style.gender == 'm':
                self.boy = 1
                self.girl = 0
            else:
                self.boy = 0
                self.girl = 1
            self.usedNames = usedNames
            if not self.addedGenderSpecific or self.oldBoy != self.boy:
                self.oldBoy = self.boy
                self.listsLoaded = 0
                self.allTitles = [
                 ' '] + [' '] + self.nameGen.boyTitles * self.boy + self.nameGen.girlTitles * self.girl + self.nameGen.neutralTitles
                self.allTitles.sort()
                self.allTitles += [
                 ' '] + [
                 ' ']
                self.allFirsts = [
                 ' '] + [' '] + self.nameGen.boyFirsts * self.boy + self.nameGen.girlFirsts * self.girl + self.nameGen.neutralFirsts
                self.allFirsts.sort()
                self.allFirsts += [
                 ' '] + [
                 ' ']
                try:
                    k = self.allFirsts.index('Von')
                    self.allFirsts[k] = 'von'
                except:
                    print "NameShop: Couldn't find von"

                self.pickANameGUIElements.remove(self.titleScrollList)
                self.pickANameGUIElements.remove(self.firstnameScrollList)
                self.titleScrollList.destroy()
                self.firstnameScrollList.destroy()
                nameShopGui = loader.loadModel('phase_3/models/gui/nameshop_gui')
                self.titleScrollList = self.makeScrollList(nameShopGui, (-0.6, 0, 0.2), (1,
                                                                                         0.8,
                                                                                         0.8,
                                                                                         1), self.allTitles, self.makeLabel, [
                 TextNode.ACenter,
                 'title'])
                self.firstnameScrollList = self.makeScrollList(nameShopGui, (-0.2,
                                                                             0, 0.2), (0.8,
                                                                                       1,
                                                                                       0.8,
                                                                                       1), self.allFirsts, self.makeLabel, [
                 TextNode.ACenter,
                 'first'])
                self.pickANameGUIElements.append(self.titleScrollList)
                self.pickANameGUIElements.append(self.firstnameScrollList)
                self.pickANameGUIElements.remove(self.titleHigh)
                self.pickANameGUIElements.remove(self.firstHigh)
                self.titleHigh.destroy()
                self.firstHigh.destroy()
                self.titleHigh = self.makeHighlight((-0.710367, 0.0, 0.122967))
                self.firstHigh = self.makeHighlight((-0.310367, 0.0, 0.122967))
                self.pickANameGUIElements.append(self.titleHigh)
                self.pickANameGUIElements.append(self.firstHigh)
                panel = nameShopGui.find('**/namePanel')
                self.namePanel = DirectFrame(parent=aspect2d, image=panel, relief='flat', scale=(0.75,
                                                                                                 0.7,
                                                                                                 0.7), state='disabled', pos=(-0.0163333,
                                                                                                                              0,
                                                                                                                              0.103267), frameColor=(1,
                                                                                                                                                     1,
                                                                                                                                                     1,
                                                                                                                                                     0))
                self.pickANameGUIElements.append(self.namePanel)
                self.nameResult.reparentTo(self.namePanel)
                self.circle = nameShopGui.find('**/namePanelCircle')
                self.titleCheck = self.makeCheckBox((-0.617, 0, 0.374), TTLocalizer.TitleCheckBox, (0,
                                                                                                    0.25,
                                                                                                    0.5,
                                                                                                    1), self.titleToggle)
                self.firstCheck = self.makeCheckBox((-0.228, 0, 0.374), TTLocalizer.FirstCheckBox, (0,
                                                                                                    0.25,
                                                                                                    0.5,
                                                                                                    1), self.firstToggle)
                self.lastCheck = self.makeCheckBox((0.382, 0, 0.374), TTLocalizer.LastCheckBox, (0,
                                                                                                 0.25,
                                                                                                 0.5,
                                                                                                 1), self.lastToggle)
                del self.circle
                self.pickANameGUIElements.append(self.titleCheck)
                self.pickANameGUIElements.append(self.firstCheck)
                self.pickANameGUIElements.append(self.lastCheck)
                self.titleCheck.wrtReparentTo(self.namePanel)
                self.firstCheck.wrtReparentTo(self.namePanel)
                self.lastCheck.wrtReparentTo(self.namePanel)
                self.titleScrollList.decButton.wrtReparentTo(self.namePanel)
                self.firstnameScrollList.decButton.wrtReparentTo(self.namePanel)
                self.lastsuffixScrollList.decButton.wrtReparentTo(self.namePanel)
                self.lastprefixScrollList.decButton.wrtReparentTo(self.namePanel)
                self.titleScrollList.incButton.wrtReparentTo(self.namePanel)
                self.firstnameScrollList.incButton.wrtReparentTo(self.namePanel)
                self.lastsuffixScrollList.incButton.wrtReparentTo(self.namePanel)
                self.lastprefixScrollList.incButton.wrtReparentTo(self.namePanel)
                self.randomButton.reparentTo(self.namePanel)
                self.typeANameButton.reparentTo(self.namePanel)
                nameShopGui.removeNode()
                self.listsLoaded = 1
                self.addedGenderSpecific = 1
                self.__randomName()
            self.typeANameButton['text'] = TTLocalizer.TypeANameButton
            if self.isLoaded == 0:
                self.load()
            self.ubershow(self.pickANameGUIElements)
            self.acceptOnce('next', self.__handleDone)
            self.acceptOnce('last', self.__handleBackward)
            self.acceptOnce('skipTutorial', self.__handleSkipTutorial)
            self.__listsChanged()
            self.fsm.request('PayState')
            return

    def __overflowNameInput(self):
        self.rejectName(TTLocalizer.NameTooLong)

    def exit(self):
        self.notify.debug('exit')
        if self.isLoaded == 0:
            return
        else:
            self.ignore('next')
            self.ignore('last')
            self.ignore('skipTutorial')
            taskMgr.remove('capNameTask')
            self.hideAll()
            return

    def __listsChanged(self):
        newname = ''
        if self.listsLoaded:
            if self.titleActive:
                self.showList(self.titleScrollList)
                self.titleHigh.show()
                newtitle = self.titleScrollList['items'][(self.titleScrollList.index + 2)]['text']
                self.nameIndices[0] = self.nameGen.returnUniqueID(newtitle, 0)
                newname += newtitle + ' '
            else:
                self.nameIndices[0] = -1
                self.stealth(self.titleScrollList)
                self.titleHigh.hide()
            if self.firstActive:
                self.showList(self.firstnameScrollList)
                self.firstHigh.show()
                newfirst = self.firstnameScrollList['items'][(self.firstnameScrollList.index + 2)]['text']
                if newfirst == 'von':
                    nt = 'Von'
                else:
                    nt = newfirst
                self.nameIndices[1] = self.nameGen.returnUniqueID(nt, 1)
                if not self.titleActive and newfirst == 'von':
                    newfirst = 'Von'
                    newname += newfirst
                else:
                    newname += newfirst
                if newfirst == 'von':
                    self.nameFlags[1] = 0
                else:
                    self.nameFlags[1] = 1
                if self.lastActive:
                    newname += ' '
            else:
                self.firstHigh.hide()
                self.stealth(self.firstnameScrollList)
                self.nameIndices[1] = -1
            if self.lastActive:
                self.showList(self.lastprefixScrollList)
                self.showList(self.lastsuffixScrollList)
                self.prefixHigh.show()
                self.suffixHigh.show()
                lp = self.lastprefixScrollList['items'][(self.lastprefixScrollList.index + 2)]['text']
                ls = self.lastsuffixScrollList['items'][(self.lastsuffixScrollList.index + 2)]['text']
                self.nameIndices[2] = self.nameGen.returnUniqueID(lp, 2)
                self.nameIndices[3] = self.nameGen.returnUniqueID(ls, 3)
                newname += lp
                if lp in self.nameGen.capPrefixes:
                    ls = ls.capitalize()
                    self.nameFlags[3] = 1
                else:
                    self.nameFlags[3] = 0
                newname += ls
            else:
                self.stealth(self.lastprefixScrollList)
                self.stealth(self.lastsuffixScrollList)
                self.prefixHigh.hide()
                self.suffixHigh.hide()
                self.nameIndices[2] = -1
                self.nameIndices[3] = -1
            self.titleIndex = self.titleScrollList.index + 2
            self.firstIndex = self.firstnameScrollList.index + 2
            self.prefixIndex = self.lastprefixScrollList.index + 2
            self.suffixIndex = self.lastsuffixScrollList.index + 2
            self.nameResult['text'] = newname
            self.names[0] = newname

    def makeScrollList(self, gui, ipos, mcolor, nitems, nitemMakeFunction, nitemMakeExtraArgs):
        self.notify.debug('makeScrollList')
        it = nitems[:]
        ds = DirectScrolledList(items=it, itemMakeFunction=nitemMakeFunction, itemMakeExtraArgs=nitemMakeExtraArgs, parent=aspect2d, relief=None, command=self.__listsChanged, pos=ipos, scale=0.6, incButton_image=(
         gui.find('**/triangleButtonUp'), gui.find('**/triangleButtonDwn'), gui.find('**/triangleButtonRllvr'),
         gui.find('**/triangleButtonUp')), incButton_relief=None, incButton_scale=(1.2,
                                                                                   1.2,
                                                                                   -1.2), incButton_pos=(0,
                                                                                                         0,
                                                                                                         -0.545), incButton_image0_color=mcolor, incButton_image1_color=mcolor, incButton_image2_color=mcolor, incButton_image3_color=Vec4(1, 1, 1, 0), decButton_image=(
         gui.find('**/triangleButtonUp'), gui.find('**/triangleButtonDwn'), gui.find('**/triangleButtonRllvr'),
         gui.find('**/triangleButtonUp')), decButton_relief=None, decButton_scale=(1.2,
                                                                                   1.2,
                                                                                   1.2), decButton_pos=(0,
                                                                                                        0,
                                                                                                        0.195), decButton_image0_color=mcolor, decButton_image1_color=mcolor, decButton_image2_color=mcolor, decButton_image3_color=Vec4(1, 1, 1, 0), itemFrame_pos=(-0.2,
                                                                                                                                                                                                                                                                     0,
                                                                                                                                                                                                                                                                     0.028), itemFrame_scale=1.0, itemFrame_relief=DGG.RAISED, itemFrame_frameSize=(-0.05,
                                                                                                                                                                                                                                                                                                                                                    0.48,
                                                                                                                                                                                                                                                                                                                                                    -0.5,
                                                                                                                                                                                                                                                                                                                                                    0.1), itemFrame_frameColor=mcolor, itemFrame_borderWidth=(0.01,
                                                                                                                                                                                                                                                                                                                                                                                                              0.01), numItemsVisible=5, forceHeight=TTLocalizer.NSdirectScrolleList)
        return ds

    def makeCheckBox(self, npos, ntex, ntexcolor, comm):
        return DirectCheckButton(parent=aspect2d, relief=None, scale=0.1, boxBorder=0.08, boxImage=self.circle, boxImageScale=4, boxImageColor=VBase4(0, 0.25, 0.5, 1), boxRelief=None, pos=npos, text=ntex, text_fg=ntexcolor, text_scale=TTLocalizer.NSmakeCheckBox, text_pos=(0.2,
                                                                                                                                                                                                                                                                                 0), indicator_pos=(-0.566667,
                                                                                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                                                                                    -0.045), indicator_image_pos=(-0.26,
                                                                                                                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                                                                                                                  0.075), command=comm, text_align=TextNode.ALeft)

    def makeHighlight(self, npos):
        return DirectFrame(parent=aspect2d, relief='flat', scale=(0.552, 0, 0.11), state='disabled', frameSize=(-0.05,
                                                                                                                0.48,
                                                                                                                -0.5,
                                                                                                                0.1), borderWidth=(0.01,
                                                                                                                                   0.01), pos=npos, frameColor=(1,
                                                                                                                                                                0,
                                                                                                                                                                1,
                                                                                                                                                                0.4))

    def titleToggle(self, value):
        self.titleActive = self.titleCheck['indicatorValue']
        if not (self.titleActive or self.firstActive or self.lastActive):
            self.titleActive = 1
        self.__listsChanged()
        if self.titleActive:
            self.titleScrollList.refresh()
        self.updateCheckBoxes()

    def firstToggle(self, value):
        self.firstActive = self.firstCheck['indicatorValue']
        if self.chastise == 2:
            messenger.send('NameShop-mickeyChange', [
             [
              TTLocalizer.ApprovalForName1,
              TTLocalizer.ApprovalForName2]])
            self.chastise = 0
        if not self.firstActive and not self.lastActive:
            self.firstActive = 1
            messenger.send('NameShop-mickeyChange', [
             [
              TTLocalizer.MustHaveAFirstOrLast1,
              TTLocalizer.MustHaveAFirstOrLast2]])
            self.chastise = 1
        self.__listsChanged()
        if self.firstActive:
            self.firstnameScrollList.refresh()
        self.updateCheckBoxes()

    def lastToggle(self, value):
        self.lastActive = self.lastCheck['indicatorValue']
        if self.chastise == 1:
            messenger.send('NameShop-mickeyChange', [
             [
              TTLocalizer.ApprovalForName1,
              TTLocalizer.ApprovalForName2]])
            self.chastise = 0
        if not self.firstActive and not self.lastActive:
            self.lastActive = 1
            messenger.send('NameShop-mickeyChange', [
             [
              TTLocalizer.MustHaveAFirstOrLast1,
              TTLocalizer.MustHaveAFirstOrLast2]])
            self.chastise = 2
        self.__listsChanged()
        if self.lastActive:
            self.lastprefixScrollList.refresh()
            self.lastsuffixScrollList.refresh()
        self.updateCheckBoxes()

    def updateCheckBoxes(self):
        self.titleCheck['indicatorValue'] = self.titleActive
        self.titleCheck.setIndicatorValue()
        self.firstCheck['indicatorValue'] = self.firstActive
        self.firstCheck.setIndicatorValue()
        self.lastCheck['indicatorValue'] = self.lastActive
        self.lastCheck.setIndicatorValue()

    def load(self):
        self.notify.debug('load')
        if self.isLoaded == 1:
            return
        else:
            nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
            guiButton = loader.loadModel('phase_3/models/gui/quit_button')
            gui = loader.loadModel('phase_3/models/gui/nameshop_gui')
            typePanel = gui.find('**/typeNamePanel')
            self.typeNamePanel = DirectFrame(parent=aspect2d, image=typePanel, relief='flat', scale=(0.75,
                                                                                                     0.7,
                                                                                                     0.7), state='disabled', pos=(-0.0163333,
                                                                                                                                  0,
                                                                                                                                  0.075), frameColor=(1,
                                                                                                                                                      1,
                                                                                                                                                      1,
                                                                                                                                                      0))
            self.typeANameGUIElements.append(self.typeNamePanel)
            self.nameLabel = OnscreenText.OnscreenText(TTLocalizer.PleaseTypeName, parent=aspect2d, style=OnscreenText.ScreenPrompt, pos=(0,
                                                                                                                                          0.53))
            self.typeANameGUIElements.append(self.nameLabel)
            self.typeNotification = OnscreenText.OnscreenText(TTLocalizer.AllNewNamesR, parent=aspect2d, style=OnscreenText.ScreenPrompt, pos=(0,
                                                                                                                                               0.15))
            self.typeANameGUIElements.append(self.typeNotification)
            tempForceCapitalization = False
            self.nameEntry = DirectEntry(parent=aspect2d, relief=None, scale=TTLocalizer.NSnameEntry, entryFont=getToonFont(), width=MAX_NAME_WIDTH, numLines=2, focus=0, cursorKeys=1, pos=(0.0,
                                                                                                                                                                                             0.0,
                                                                                                                                                                                             0.39), text_align=TextNode.ACenter, command=self.__typedAName, autoCapitalize=tempForceCapitalization)
            self.typeANameGUIElements.append(self.nameEntry)
            self.submitButton = DirectButton(parent=aspect2d, relief=None, image=(
             guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(1.2,
                                                                                                                                0,
                                                                                                                                1.1), pos=(-0.01,
                                                                                                                                           0,
                                                                                                                                           -0.25), text=TTLocalizer.NameShopSubmitButton, text_scale=0.06, text_pos=(0,
                                                                                                                                                                                                                     -0.02), command=self.__typedAName)
            self.typeANameGUIElements.append(self.submitButton)
            self.randomButton = DirectButton(parent=aspect2d, relief=None, image=(
             guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(1.15,
                                                                                                                                1.1,
                                                                                                                                1.1), scale=(1.4,
                                                                                                                                             1,
                                                                                                                                             1.4), pos=(0.01,
                                                                                                                                                        0,
                                                                                                                                                        -0.5), text=TTLocalizer.RandomButton, text_scale=0.06, text_pos=(0,
                                                                                                                                                                                                                         -0.02), command=self.__randomName)
            self.pickANameGUIElements.append(self.randomButton)
            self.typeANameButton = DirectButton(parent=aspect2d, relief=None, image=(
             guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), image_scale=(1,
                                                                                                                                1.1,
                                                                                                                                0.9), pos=(0.01,
                                                                                                                                           0,
                                                                                                                                           -0.695), scale=(1.6,
                                                                                                                                                           1,
                                                                                                                                                           1.7), text=TTLocalizer.TypeANameButton, text_scale=TTLocalizer.NStypeANameButton, text_pos=(
             0, TTLocalizer.NStypeANameButton_pos), command=self.__typeAName)
            if base.cr.productName in ('ES', 'DE', 'BR'):
                self.typeANameButton.hide()
            self.pickANameGUIElements.append(self.typeANameButton)
            self.nameResult = DirectLabel(parent=aspect2d, relief=None, scale=TTLocalizer.NSnameResultRetro, pos=(0.04,
                                                                                                                  0,
                                                                                                                  0.7), text=' \n ', text_scale=0.8, text_align=TextNode.ACenter, text_wordwrap=MAX_NAME_WIDTH)
            self.pickANameGUIElements.append(self.nameResult)
            self.allPrefixes = self.nameGen.lastPrefixes[:]
            self.allSuffixes = self.nameGen.lastSuffixes[:]
            self.allPrefixes.sort()
            self.allSuffixes.sort()
            self.allPrefixes = [
             ' '] + [' '] + self.allPrefixes + [' '] + [
             ' ']
            self.allSuffixes = [
             ' '] + [' '] + self.allSuffixes + [' '] + [
             ' ']
            self.titleScrollList = self.makeScrollList(gui, (-0.6, 0, 0.2), (1, 0.8,
                                                                             0.8,
                                                                             1), self.allTitles, self.makeLabel, [
             TextNode.ACenter,
             'title'])
            self.firstnameScrollList = self.makeScrollList(gui, (-0.2, 0, 0.2), (0.8,
                                                                                 1,
                                                                                 0.8,
                                                                                 1), self.allFirsts, self.makeLabel, [
             TextNode.ACenter,
             'first'])
            self.lastprefixScrollList = self.makeScrollList(gui, (0.2, 0, 0.2), (0.8,
                                                                                 0.8,
                                                                                 1,
                                                                                 1), self.allPrefixes, self.makeLabel, [
             TextNode.ARight,
             'prefix'])
            self.lastsuffixScrollList = self.makeScrollList(gui, (0.55, 0, 0.2), (0.8,
                                                                                  0.8,
                                                                                  1,
                                                                                  1), self.allSuffixes, self.makeLabel, [
             TextNode.ALeft,
             'suffix'])
            gui.removeNode()
            self.pickANameGUIElements.append(self.lastprefixScrollList)
            self.pickANameGUIElements.append(self.lastsuffixScrollList)
            self.pickANameGUIElements.append(self.titleScrollList)
            self.pickANameGUIElements.append(self.firstnameScrollList)
            self.titleHigh = self.makeHighlight((-0.710367, 0.0, 0.122967))
            self.firstHigh = self.makeHighlight((-0.310367, 0.0, 0.122967))
            self.pickANameGUIElements.append(self.titleHigh)
            self.pickANameGUIElements.append(self.firstHigh)
            self.prefixHigh = self.makeHighlight((0.09, 0.0, 0.122967))
            self.suffixHigh = self.makeHighlight((0.44, 0.0, 0.122967))
            self.pickANameGUIElements.append(self.prefixHigh)
            self.pickANameGUIElements.append(self.suffixHigh)
            nameBalloon.removeNode()
            imageList = (
             guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
            buttonImage = [
             imageList,
             imageList]
            buttonText = [
             TTLocalizer.NameShopPay,
             TTLocalizer.NameShopPlay]
            self.payDialog = DirectDialog(dialogName='paystate', topPad=0, fadeScreen=0.2, pos=(0,
                                                                                                0.1,
                                                                                                0.1), button_relief=None, text_align=TextNode.ACenter, text=TTLocalizer.NameShopOnlyPaid, buttonTextList=buttonText, buttonImageList=buttonImage, image_color=GlobalDialogColor, buttonValueList=[
             1,
             0], command=self.payAction)
            self.payDialog.buttonList[0].setPos(0, 0, -0.27)
            self.payDialog.buttonList[1].setPos(0, 0, -0.4)
            self.payDialog.buttonList[0]['image_scale'] = (1.2, 1, 1.1)
            self.payDialog.buttonList[1]['image_scale'] = (1.2, 1, 1.1)
            self.payDialog['image_scale'] = (0.8, 1, 0.77)
            self.payDialog.buttonList[0]['text_pos'] = (0, -0.02)
            self.payDialog.buttonList[1]['text_pos'] = (0, -0.02)
            self.payDialog.hide()
            buttonText = [
             TTLocalizer.NameShopContinueSubmission,
             TTLocalizer.NameShopChooseAnother]
            self.approvalDialog = DirectDialog(relief=None, image=DGG.getDefaultDialogGeom(), dialogName='approvalstate', topPad=0, fadeScreen=0.2, pos=(0,
                                                                                                                                                         0.1,
                                                                                                                                                         0.1), button_relief=None, image_color=GlobalDialogColor, text_align=TextNode.ACenter, text=TTLocalizer.NameShopToonCouncil, buttonTextList=buttonText, buttonImageList=buttonImage, buttonValueList=[1, 0], command=self.approvalAction)
            self.approvalDialog.buttonList[0].setPos(0, 0, -0.3)
            self.approvalDialog.buttonList[1].setPos(0, 0, -0.43)
            self.approvalDialog['image_scale'] = (0.8, 1, 0.77)
            for x in range(0, 2):
                self.approvalDialog.buttonList[x]['text_pos'] = (0, -0.01)
                self.approvalDialog.buttonList[x]['text_scale'] = (0.04, 0.05999)
                self.approvalDialog.buttonList[x].setScale(1.2, 1, 1)

            self.approvalDialog.hide()
            guiButton.removeNode()
            self.uberhide(self.typeANameGUIElements)
            self.uberhide(self.pickANameGUIElements)
            self.isLoaded = 1
            return

    def ubershow(self, guiObjectsToShow):
        self.notify.debug('ubershow %s' % str(guiObjectsToShow))
        for x in guiObjectsToShow:
            try:
                x.show()
            except:
                print 'NameShop: Tried to show already removed object'

        if base.cr.productName in ('ES', 'DE', 'BR'):
            self.typeANameButton.hide()

    def hideAll(self):
        self.uberhide(self.pickANameGUIElements)
        self.uberhide(self.typeANameGUIElements)

    def uberhide(self, guiObjectsToHide):
        self.notify.debug('uberhide %s' % str(guiObjectsToHide))
        for x in guiObjectsToHide:
            try:
                x.hide()
            except:
                print 'NameShop: Tried to hide already removed object'

    def uberdestroy(self, guiObjectsToDestroy):
        self.notify.debug('uberdestroy %s' % str(guiObjectsToDestroy))
        for x in guiObjectsToDestroy:
            try:
                x.destroy()
                del x
            except:
                print 'NameShop: Tried to destroy already removed object'

    def getNameIndices(self):
        return self.nameIndices

    def getNameFlags(self):
        return self.nameFlags

    def getNameAction(self):
        return self.nameAction

    def unload(self):
        self.notify.debug('unload')
        if self.isLoaded == 0:
            return
        else:
            self.exit()
            cleanupDialog('globalDialog')
            self.uberdestroy(self.pickANameGUIElements)
            self.uberdestroy(self.typeANameGUIElements)
            del self.toon
            self.payDialog.cleanup()
            self.approvalDialog.cleanup()
            del self.payDialog
            del self.approvalDialog
            self.parentFSM.getStateNamed('NameShop').removeChild(self.fsm)
            del self.parentFSM
            del self.fsm
            self.ignoreAll()
            self.isLoaded = 0
            return

    def _checkNpcNames(self, name):

        def match(npcName, name=name):
            return TextEncoder.upper(npcName) == TextEncoder.upper(string.strip(name))

        for npcId in NPCToons.NPCToonDict.keys():
            npcName = NPCToons.NPCToonDict[npcId][1]
            if match(npcName):
                self.notify.info('name matches NPC name "%s"' % npcName)
                return TTLocalizer.NCGeneric

    def nameIsValid(self, name):
        self.notify.debug('nameIsValid')
        if name in self.usedNames:
            return TTLocalizer.ToonAlreadyExists % name
        problem = NameCheck.checkName(name, [
         self._checkNpcNames])
        if problem:
            return problem

    def setShopsVisited(self, list):
        self.shopsVisited = list

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def __handleChastised(self):
        self.chastiseDialog.cleanup()

    def __createAvatar(self, skipTutorial=False, *args):
        self.notify.debug('__createAvatar')
        if self.fsm.getCurrentState().getName() == 'TypeAName':
            self.__typedAName()
            return
        else:
            if not self.avExists or self.avExists and self.avId == 'deleteMe':
                self.serverCreateAvatar(skipTutorial)
            elif self.names[0] == '':
                self.rejectName(TTLocalizer.EmptyNameError)
            else:
                rejectReason = self.nameIsValid(self.names[0])
                if rejectReason != None:
                    self.rejectName(rejectReason)
                else:
                    self.checkNamePattern()
            return

    def acceptName(self):
        self.notify.debug('acceptName')
        self.toon.setName(self.names[0])
        self.doneStatus = 'done'
        self.storeSkipTutorialRequest()
        messenger.send(self.doneEvent)

    def rejectName(self, str):
        self.notify.debug('rejectName')
        self.names[0] = ''
        self.rejectDialog = TTDialog.TTGlobalDialog(doneEvent='rejectDone', message=str, style=TTDialog.Acknowledge)
        self.rejectDialog.show()
        if str == TTLocalizer.NameUnintendedError:
            self.acceptOnce('rejectDone', base.userExit)
        else:
            self.acceptOnce('rejectDone', self.__handleReject)

    def __handleReject(self):
        self.rejectDialog.cleanup()
        self.nameEntry['focus'] = 1
        self.typeANameButton.show()
        self.acceptOnce('next', self.__createAvatar)

    def restoreIndexes(self, oi):
        self.titleIndex = oi[0]
        self.firstIndex = oi[1]
        self.prefixIndex = oi[2]
        self.suffixIndex = oi[3]

    def stealth(self, listToDo):
        listToDo.decButton['state'] = 'disabled'
        listToDo.incButton['state'] = 'disabled'
        for item in listToDo['items']:
            if item.__class__.__name__ != 'str':
                item.hide()

    def showList(self, listToDo):
        listToDo.show()
        listToDo.decButton['state'] = 'normal'
        listToDo.incButton['state'] = 'normal'

    def updateLists(self):
        oldindex = [
         self.titleIndex,
         self.firstIndex,
         self.prefixIndex,
         self.suffixIndex]
        self.titleScrollList.scrollTo(self.titleIndex - 2)
        self.restoreIndexes(oldindex)
        self.firstnameScrollList.scrollTo(self.firstIndex - 2)
        self.restoreIndexes(oldindex)
        self.lastprefixScrollList.scrollTo(self.prefixIndex - 2)
        self.restoreIndexes(oldindex)
        self.lastsuffixScrollList.scrollTo(self.suffixIndex - 2)
        self.restoreIndexes(oldindex)

    def __randomName(self):
        self.notify.debug('Finding random name')
        uberReturn = self.nameGen.randomNameMoreinfo(self.boy, self.girl)
        self.names[0] = uberReturn[(len(uberReturn) - 1)]
        self.titleActive = 0
        self.firstActive = 0
        self.lastActive = 0
        if uberReturn[0]:
            self.titleActive = 1
        if uberReturn[1]:
            self.firstActive = 1
        if uberReturn[2]:
            self.lastActive = 1
        try:
            self.titleIndex = self.allTitles.index(uberReturn[3])
            self.nameIndices[0] = self.nameGen.returnUniqueID(uberReturn[3], 0)
            self.nameFlags[0] = 1
        except:
            print 'NameShop : Should have found title, uh oh!'
            print uberReturn

        try:
            self.firstIndex = self.allFirsts.index(uberReturn[4])
            self.nameIndices[1] = self.nameGen.returnUniqueID(uberReturn[4], 1)
            self.nameFlags[1] = 1
        except:
            print 'NameShop : Should have found first name, uh oh!'
            print uberReturn

        try:
            self.prefixIndex = self.allPrefixes.index(uberReturn[5])
            self.suffixIndex = self.allSuffixes.index(uberReturn[6].lower())
            self.nameIndices[2] = self.nameGen.returnUniqueID(uberReturn[5], 2)
            self.nameIndices[3] = self.nameGen.returnUniqueID(uberReturn[6].lower(), 3)
            if uberReturn[5] in self.nameGen.capPrefixes:
                self.nameFlags[3] = 1
            else:
                self.nameFlags[3] = 0
        except:
            print 'NameShop : Some part of last name not found, uh oh!'
            print uberReturn

        self.updateCheckBoxes()
        self.updateLists()
        self.nameResult['text'] = self.names[0]

    def findTempName(self):
        colorstring = TTLocalizer.NumToColor[self.toon.style.headColor]
        animaltype = TTLocalizer.AnimalToSpecies[self.toon.style.getAnimal()]
        tempname = colorstring + ' ' + animaltype
        if not TTLocalizer.NScolorPrecede:
            tempname = animaltype + ' ' + colorstring
        self.names[0] = tempname
        tempname = '"' + tempname + '"'
        return tempname

    def enterInit(self):
        self.notify.debug('enterInit')

    def exitInit(self):
        pass

    def enterPayState(self):
        self.notify.debug('enterPayState')
        if base.cr.allowFreeNames() or self.isPaid:
            self.fsm.request('PickAName')
        else:
            tempname = self.findTempName()
            self.payDialog['text'] = TTLocalizer.NameShopOnlyPaid + tempname
            self.payDialog.show()

    def exitPayState(self):
        pass

    def payAction(self, value):
        self.notify.debug('payAction')
        self.payDialog.hide()
        if value:
            self.doneStatus = 'paynow'
            messenger.send(self.doneEvent)
        else:
            self.nameAction = 0
            self.__createAvatar()

    def enterPickANameState(self):
        self.notify.debug('enterPickANameState')
        self.ubershow(self.pickANameGUIElements)
        self.nameAction = 1
        self.__listsChanged()

    def exitPickANameState(self):
        self.uberhide(self.pickANameGUIElements)

    def enterTypeANameState(self):
        self.notify.debug('enterTypeANameState')
        self.ubershow(self.typeANameGUIElements)
        self.typeANameButton.show()
        self.nameEntry.set('')
        self.nameEntry['focus'] = 1

    def __typeAName(self):
        if base.restrictTrialers:
            if not base.cr.isPaid():
                dialog = TeaserPanel.TeaserPanel(pageName='typeAName')
                return
        if self.fsm.getCurrentState().getName() == 'TypeAName':
            self.typeANameButton['text'] = TTLocalizer.TypeANameButton
            self.typeANameButton.wrtReparentTo(self.namePanel)
            self.fsm.request('PickAName')
        else:
            self.typeANameButton['text'] = TTLocalizer.PickANameButton
            self.typeANameButton.wrtReparentTo(aspect2d)
            self.typeANameButton.show()
            self.fsm.request('TypeAName')
            taskMgr.add(self.__capNameTask, 'capNameTask')
        return

    def __capNameTask(self, task):
        self.__capName()
        return Task.cont

    def __capName(self):
        name = self.nameEntry.get()
        capName = ''
        for i in xrange(len(name)):
            letter = name[i]
            if letter in string.letters:
                if i == 0 or name[(i - 1)] not in string.letters:
                    letter = string.upper(letter)
            capName += letter

        self.nameEntry.enterText(capName)

    def __typedAName(self, *args):
        self.notify.debug('__typedAName')
        self.nameEntry['focus'] = 0
        name = self.nameEntry.get()
        name = TextEncoder().decodeText(name)
        name = name.strip()
        name = TextEncoder().encodeWtext(name)
        self.nameEntry.enterText(name)
        if not self.nameEntry.get():
            self.rejectName(TTLocalizer.NoNameWarning)
            return
        if False:
            problem = self.nameIsValid(self.nameEntry.get())
            if problem:
                self.rejectName(problem)
                return
        self.checkNameTyped(justCheck=True)

    def exitTypeANameState(self):
        self.typeANameButton.wrtReparentTo(self.namePanel)
        self.uberhide(self.typeANameGUIElements)

    def enterApprovalState(self):
        self.notify.debug('enterApprovalState')
        tempname = self.findTempName()
        self.approvalDialog['text'] = TTLocalizer.NameShopToonCouncil + tempname
        self.approvalDialog.show()

    def approvalAction(self, value):
        self.notify.debug('approvalAction')
        self.approvalDialog.hide()
        if value:
            self.nameAction = 2
            if not self.newwarp:
                self.__isFirstTime()
            else:
                self.serverCreateAvatar()
        else:
            self.typeANameButton['text'] = TTLocalizer.TypeANameButton
            self.fsm.request('PickAName')

    def sendDeleteAvatarMsgCancelStyle(self, avId):
        datagram = PyDatagram()
        datagram.addUint16(CLIENT_DELETE_AVATAR)
        datagram.addUint32(avId)
        messenger.send('nameShopPost', [
         datagram])

    def exitApprovalState(self):
        pass

    def enterAcceptedState(self):
        self.notify.debug('enterAcceptedState')
        self.acceptedDialog = TTDialog.TTGlobalDialog(doneEvent='acceptedDone', message=TTLocalizer.NameShopNameAccepted, style=TTDialog.Acknowledge)
        self.acceptedDialog.show()
        self.acceptOnce('acceptedDone', self.__handleAccepted)

    def enterApprovalAcceptedState(self):
        self.notify.debug('enterApprovalAcceptedState')
        self.doneStatus = 'done'
        self.storeSkipTutorialRequest()
        messenger.send(self.doneEvent)

    def exitApprovalAcceptedState(self):
        pass

    def __handleAccepted(self):
        self.acceptedDialog.cleanup()
        if self.avExists:
            self.checkNameTyped(rename=True)
        else:
            self.nameAction = 3
            if not self.newwarp:
                self.__isFirstTime()
            else:
                self.serverCreateAvatar()

    def __handleDoneRename(self, avId, status):
        self.cleanupWaitForServer()
        if status not in (0, 1, 2):
            self.rejectName(TTLocalizer.NameUnintendedError)
        else:
            self.doneStatus = 'done'
            self.storeSkipTutorialRequest()
            messenger.send(self.doneEvent)

    def __handleAcceptedDone(self):
        self.acceptedDialog.cleanup()

    def exitAcceptedState(self):
        pass

    def enterRejectedState(self):
        self.notify.debug('enterRejectedState')
        self.rejectedDialog = TTDialog.TTGlobalDialog(doneEvent='rejectedDone', message=TTLocalizer.NameShopNameRejected, style=TTDialog.Acknowledge)
        self.rejectedDialog.show()
        self.acceptOnce('rejectedDone', self.__handleRejected)

    def __handleRejected(self):
        self.rejectedDialog.cleanup()
        self.fsm.request('TypeAName')

    def exitRejectedState(self):
        pass

    def enterDone(self):
        self.notify.debug('enterDone')

    def exitDone(self):
        pass

    def nameShopHandler(self, msgType, di):
        self.notify.debug('nameShopHandler')
        if msgType == CLIENT_CREATE_AVATAR_RESP:
            self.handleCreateAvatarResponseMsg(di)
        return

    def checkNamePattern(self):
        self.notify.debug('checkNamePattern')
        base.cr.gameServicesManager.sendSetNamePattern(self.avId, self.nameIndices[0], self.nameFlags[0], self.nameIndices[1], self.nameFlags[1], self.nameIndices[2], self.nameFlags[2], self.nameIndices[3], self.nameFlags[3], self.handleSetNamePatternResp)
        self.waitForServer()

    def __handleDone(self):
        if self.fsm.getCurrentState().getName() == 'TypeAName':
            self.__typedAName()
        else:
            self.__isFirstTime()

    def handleSetNamePatternResp(self, avId, status):
        self.notify.debug('handleSetNamePatternResp')
        self.cleanupWaitForServer()
        if avId != self.avId:
            self.notify.debug("doid's don't match up!")
            self.rejectName(TTLocalizer.NameError)
        if status == 1:
            style = self.toon.getStyle()
            avDNA = style.makeNetString()
            self.notify.debug('pattern name accepted')
            newPotAv = PotentialAvatar.PotentialAvatar(avId, self.names, avDNA, self.index, 0)
            self.avList.append(newPotAv)
            self.doneStatus = 'done'
            self.storeSkipTutorialRequest()
            messenger.send(self.doneEvent)
        else:
            self.notify.debug('name pattern rejected')
            self.rejectName(TTLocalizer.NameError)
        return

    def checkNameTyped(self, justCheck=False, rename=False):
        self.notify.debug('checkNameTyped')
        if self._submitTypeANameAsPickAName():
            return
        if justCheck:
            avId = 0
        else:
            avId = self.avId
        if rename:
            base.cr.gameServicesManager.sendSetNameTyped(avId, self.nameEntry.get(), self.__handleDoneRename)
            self.waitForServer()
        else:
            base.cr.gameServicesManager.sendSetNameTyped(avId, self.nameEntry.get(), self.handleNameTypedResponse)
            self.waitForServer()

    def handleNameTypedResponse(self, avId, status):
        self.notify.debug('handleNameTypedResponse')
        self.cleanupWaitForServer()
        if avId and avId != self.avId:
            self.notify.debug("doid's don't match up!")
            self.rejectName(TTLocalizer.NameError)
        if avId == 0:
            if status == 2:
                self.notify.debug('name check accepted')
                self.fsm.request('Accepted')
            elif status == 1:
                self.notify.debug('name check pending')
                self.fsm.request('Approval')
            elif status == 0:
                self.notify.debug('name check rejected')
                self.fsm.request('TypeAName')
                self.rejectName(TTLocalizer.NameError)
            else:
                self.notify.debug('typed name response did not contain any return fields')
                self.rejectName(TTLocalizer.NameError)
        elif status == 2:
            style = self.toon.getStyle()
            avDNA = style.makeNetString()
            newPotAv = PotentialAvatar.PotentialAvatar(avId, (self.nameEntry.get(), '', '', ''), avDNA, self.index, 1, wishState='LOCKED')
            self.avList.append(newPotAv)
            self.fsm.request('Accepted')
        elif status == 1:
            style = self.toon.getStyle()
            avDNA = style.makeNetString()
            self.names[1] = self.nameEntry.get()
            self.notify.debug('typed name needs approval')
            newPotAv = PotentialAvatar.PotentialAvatar(avId, self.names, avDNA, self.index, 1)
            if not self.newwarp:
                self.avList.append(newPotAv)
            self.fsm.request('ApprovalAccepted')
        elif status == 0:
            self.fsm.request('Rejected')
        else:
            self.notify.debug("name typed accepted but didn't fill any return fields")
            self.rejectName(TTLocalizer.NameError)

    def _updateGuiWithPickAName(self, flags, names, fullName):
        uberReturn = flags + names + [fullName]
        self.names[0] = uberReturn[(len(uberReturn) - 1)]
        self.titleActive = 0
        self.firstActive = 0
        self.lastActive = 0
        if uberReturn[0]:
            self.titleActive = 1
        if uberReturn[1]:
            self.firstActive = 1
        if uberReturn[2]:
            self.lastActive = 1
        try:
            self.titleIndex = self.allTitles.index(uberReturn[3])
            self.nameIndices[0] = self.nameGen.returnUniqueID(uberReturn[3], 0)
            self.nameFlags[0] = 1
        except:
            print 'NameShop : Should have found title, uh oh!'
            print uberReturn

        try:
            self.firstIndex = self.allFirsts.index(uberReturn[4])
            self.nameIndices[1] = self.nameGen.returnUniqueID(uberReturn[4], 1)
            self.nameFlags[1] = 1
        except:
            print 'NameShop : Should have found first name, uh oh!'
            print uberReturn

        try:
            self.prefixIndex = self.allPrefixes.index(uberReturn[5])
            self.suffixIndex = self.allSuffixes.index(uberReturn[6].lower())
            self.nameIndices[2] = self.nameGen.returnUniqueID(uberReturn[5], 2)
            self.nameIndices[3] = self.nameGen.returnUniqueID(uberReturn[6].lower(), 3)
            if uberReturn[5] in self.nameGen.capPrefixes:
                self.nameFlags[3] = 1
            else:
                self.nameFlags[3] = 0
        except:
            print 'NameShop : Some part of last name not found, uh oh!'
            print uberReturn

        self.updateCheckBoxes()
        self.updateLists()
        self.nameResult['text'] = self.names[0]

    def _submitTypeANameAsPickAName(self):
        pnp = TTPickANamePattern(self.nameEntry.get(), self.toon.style.gender)
        if pnp.hasNamePattern():
            pattern = pnp.getNamePattern()
            self.fsm.request('PickAName')
            flags = [pattern[0] != -1, pattern[1] != -1, pattern[2] != -1]
            names = []
            for i in xrange(len(pattern)):
                if pattern[i] != -1:
                    names.append(pnp.getNamePartString(self.toon.style.gender, i, pattern[i]))
                else:
                    names.append('')

            fullName = pnp.getNameString(pattern, self.toon.style.gender)
            self._updateGuiWithPickAName(flags, names, fullName)
            self.__handleDone()
            return True
        return False

    def handleSetNameTypedResp(self, avId, status):
        self.notify.debug('handleSetNameTypedResp')
        self.cleanupWaitForServer()
        if avId and avId != self.avId:
            self.notify.debug("doid's don't match up!")
            self.rejectName(TTLocalizer.NameError)
        if avId == 0:
            if status == 1:
                self.notify.debug('name check pending')
                self.fsm.request('Approval')
            elif status == 2:
                self.notify.debug('name check accepted')
                self.fsm.request('Accepted')
            elif status == 0:
                self.notify.debug('name check rejected')
                self.fsm.request('TypeAName')
                self.rejectName(TTLocalizer.NameError)
            else:
                self.notify.debug('typed name response did not contain any return fields')
                self.rejectName(TTLocalizer.NameError)
        elif status == 1:
            style = self.toon.getStyle()
            avDNA = style.makeNetString()
            self.names[1] = self.nameEntry.get()
            self.notify.debug('typed name needs approval')
            newPotAv = PotentialAvatar.PotentialAvatar(avId, self.names, avDNA, self.index, 1)
            if not self.newwarp:
                self.avList.append(newPotAv)
            self.fsm.request('ApprovalAccepted')
        elif status == 2:
            style = self.toon.getStyle()
            avDNA = style.makeNetString()
            self.toon.setName(self.names[0])
            newPotAv = PotentialAvatar.PotentialAvatar(avId, self.names, avDNA, self.index, 1)
            if not self.newwarp:
                self.avList.append(newPotAv)
            self.fsm.request('ApprovalAccepted')
        elif status == 0:
            self.fsm.request('Rejected')
        else:
            self.notify.debug("name typed accepted but didn't fill any return fields")
            self.rejectName(TTLocalizer.NameError)

    def serverCreateAvatar(self, skipTutorial=False):
        self.notify.debug('serverCreateAvatar')
        style = self.toon.getStyle()
        self.newDNA = style.makeNetString()
        if skipTutorial:
            self.requestingSkipTutorial = True
        else:
            self.requestingSkipTutorial = False
        if not self.avExists or self.avExists and self.avId == 'deleteMe':
            if self.nameAction == 3:
                base.cr.gameServicesManager.sendCreateAvatar(style, self.nameEntry.get(), self.index)
            else:
                base.cr.gameServicesManager.sendCreateAvatar(style, '', self.index)
            self.accept('nameShopCreateAvatarDone', self.handleCreateAvatarResponse)
        else:
            self.checkNameTyped()
        self.notify.debug('Ending Make A Toon: %s' % self.toon.style)
        print 'cooldude ' + style.torso
        base.cr.centralLogger.writeClientEvent('MAT - endingMakeAToon: %s' % self.toon.style)

    def handleCreateAvatarResponse(self, avId):
        self.notify.debug('handleCreateAvatarResponse')
        self.notify.debug('avatar with default name accepted')
        self.avId = avId
        self.avExists = 1
        self.logAvatarCreation()
        if self.nameAction == 0:
            self.toon.setName(self.names[0])
            newPotAv = PotentialAvatar.PotentialAvatar(self.avId, self.names, self.newDNA, self.index, 1)
            self.avList.append(newPotAv)
            self.doneStatus = 'done'
            self.storeSkipTutorialRequest()
            messenger.send(self.doneEvent)
        elif self.nameAction == 1:
            self.checkNamePattern()
        elif self.nameAction == 2:
            self.checkNameTyped()
        elif self.nameAction == 3:
            self.toon.setName(self.nameEntry.get())
            newPotAv = PotentialAvatar.PotentialAvatar(self.avId, (self.nameEntry.get(), '', '', ''), self.newDNA, self.index, 1, wishState='LOCKED')
            self.avList.append(newPotAv)
            self.doneStatus = 'done'
            self.storeSkipTutorialRequest()
            messenger.send(self.doneEvent)
        else:
            self.notify.debug('avatar invalid nameAction')
            self.rejectName(TTLocalizer.NameError)

    def waitForServer(self):
        self.waitForServerDialog = TTDialog.TTDialog(text=TTLocalizer.WaitingForNameSubmission, style=TTDialog.NoButtons)
        self.waitForServerDialog.show()

    def cleanupWaitForServer(self):
        if self.waitForServerDialog != None:
            self.waitForServerDialog.cleanup()
            self.waitForServerDialog = None
        return

    def printTypeANameInfo(self, str):
        sourceFilename, lineNumber, functionName = PythonUtil.stackEntryInfo(1)
        self.notify.debug('========================================\n%s : %s :  %s' % (sourceFilename, lineNumber, functionName))
        self.notify.debug(str)
        curPos = self.typeANameButton.getPos()
        self.notify.debug('Pos = %.2f %.2f %.2f' % (curPos[0], curPos[1], curPos[2]))
        parent = self.typeANameButton.getParent()
        parentPos = parent.getPos()
        self.notify.debug('Parent = %s' % parent)
        self.notify.debug('ParentPos = %.2f %.2f %.2f' % (parentPos[0], parentPos[1], parentPos[2]))

    def __isFirstTime(self):
        if self.parentFSM.warp:
            self.__createAvatar()
        elif base.cr.moddingManager.getDefaultMaxToon():
            self.promptMaxToon()
        else:
            self.promptTutorial()

    def promptTutorial(self):
        self.promptTutorialDialog = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.PromptTutorial, text_scale=0.06, text_align=TextNode.ACenter, text_wordwrap=22, command=self.__openTutorialDialog, fadeScreen=0.5, style=TTDialog.TwoChoice, buttonTextList=[
         TTLocalizer.MakeAToonEnterTutorial,
         TTLocalizer.MakeAToonSkipTutorial], button_text_scale=0.06, buttonPadSF=5.5, sortOrder=DGG.NO_FADE_SORT_INDEX)
        self.promptTutorialDialog.show()

    def __openTutorialDialog(self, choice=0):
        if choice == 1:
            self.notify.debug('enterTutorial')
            if config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: ENTERTUTORIAL: Enter Tutorial')
            self.__createAvatar()
        else:
            self.notify.debug('skipTutorial')
            if config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: SKIPTUTORIAL: Skip Tutorial')
            self.__handleSkipTutorial()
        self.promptTutorialDialog.destroy()

    def promptMaxToon(self):
        self.promptMaxToonDialog = TTDialog.TTDialog(parent=aspect2dp, text=TTLocalizer.PromptMaxToon, text_scale=0.06, text_align=TextNode.ACenter, text_wordwrap=22, command=self.__openMaxToonDialog, fadeScreen=0.5, style=TTDialog.Acknowledge, sortOrder=DGG.NO_FADE_SORT_INDEX)
        self.promptMaxToonDialog.show()

    def __openMaxToonDialog(self, state):
        self.notify.debug('skipTutorial - maxToon')
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: SKIPTUTORIAL: Skip Tutorial - Max Toon')
        self.__handleSkipTutorial()
        self.promptMaxToonDialog.destroy()

    def __handleSkipTutorial(self):
        self.__createAvatar(skipTutorial=True)

    def logAvatarCreation(self):
        dislId = 0
        try:
            dislId = launcher.getValue('GAME_DISL_ID')
        except:
            pass

        if not dislId:
            self.notify.warning('No dislId, using 0')
            dislId = 0
        gameSource = '0'
        try:
            gameSource = launcher.getValue('GAME_SOURCE')
        except:
            pass

        if not gameSource:
            gameSource = '0'
        else:
            self.notify.info('got GAME_SOURCE=%s' % gameSource)
        if self.avId > 0:
            base.cr.centralLogger.writeClientEvent('createAvatar %s-%s-%s' % (self.avId, dislId, gameSource))
            self.notify.debug('createAvatar %s-%s-%s' % (self.avId, dislId, gameSource))
        else:
            self.notify.warning('logAvatarCreation got self.avId =%s' % self.avId)

    def storeSkipTutorialRequest(self):
        base.cr.skipTutorialRequest = self.requestingSkipTutorial