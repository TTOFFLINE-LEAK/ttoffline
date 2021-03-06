import time
from direct.showbase import DirectObject
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from panda3d.core import *
from toontown.toon import ToonDNA
from toontown.toon import ToonHead
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
from toontown.toontowngui import TeaserPanel
from toontown.toonbase import ToontownGlobals
NAME_ROTATIONS = (7, -11, 1, -5, 3.5, -5)
NAME_POSITIONS = ((0, 0, 0.26),
 (-0.03, 0, 0.25),
 (0, 0, 0.27),
 (-0.03, 0, 0.25),
 (0.03, 0, 0.26),
 (0, 0, 0.26))
DELETE_POSITIONS = ((0.187, 0, -0.26),
 (0.31, 0, -0.167),
 (0.231, 0, -0.241),
 (0.314, 0, -0.186),
 (0.243, 0, -0.233),
 (0.28, 0, -0.207))

class AvatarChoice(DirectButton):
    notify = DirectNotifyGlobal.directNotify.newCategory('AvatarChoice')
    NEW_TRIALER_OPEN_POS = (1, )
    OLD_TRIALER_OPEN_POS = (1, 4)
    MODE_CREATE = 0
    MODE_CHOOSE = 1
    MODE_LOCKED = 2

    def __init__(self, av=None, position=0, paid=0, okToLockout=1):
        DirectButton.__init__(self, relief=None, text='', text_font=ToontownGlobals.getSignFont())
        self.initialiseoptions(AvatarChoice)
        self.hasPaid = paid
        self.mode = None
        if base.restrictTrialers and okToLockout:
            if position not in AvatarChoice.NEW_TRIALER_OPEN_POS:
                if not self.hasPaid:
                    self.mode = AvatarChoice.MODE_LOCKED
                    self.name = ''
                    self.dna = None
        if self.mode is not AvatarChoice.MODE_LOCKED:
            if not av:
                self.mode = AvatarChoice.MODE_CREATE
                self.name = ''
                self.dna = None
            else:
                self.mode = AvatarChoice.MODE_CHOOSE
                self.name = av.name
                self.dna = ToonDNA.ToonDNA(av.dna)
                self.wantName = av.wantName
                self.approvedName = av.approvedName
                self.rejectedName = av.rejectedName
                self.allowedName = av.allowedName
        self.position = position
        self.doneEvent = 'avChoicePanel-' + str(self.position)
        self.deleteWithPasswordFrame = None
        if config.GetBool('want-retro-mode', False):
            self.pickAToonGui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        else:
            if base.cr.isHalloween:
                self.pickAToonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_halloween')
            else:
                if base.cr.isWinter:
                    self.pickAToonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui_christmas')
                else:
                    self.pickAToonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')
        self.buttonBgs = []
        if config.GetBool('want-retro-mode', False):
            self['image'] = self.pickAToonGui.find('**/av-chooser_Square_UP')
        else:
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squareRed'))
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squareGreen'))
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squarePurple'))
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squareBlue'))
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squarePink'))
            self.buttonBgs.append(self.pickAToonGui.find('**/tt_t_gui_pat_squareYellow'))
            self['image'] = self.buttonBgs[position]
        self.setScale(1.01)
        if self.mode is AvatarChoice.MODE_LOCKED:
            self['command'] = self.__handleTrialer
            self['text'] = TTLocalizer.AvatarChoiceSubscribersOnly
            if config.GetBool('want-retro-mode', False):
                self['text0_scale'] = 0.1
                self['text1_scale'] = 0.115
                self['text2_scale'] = 0.115
                self['text0_fg'] = (0, 1, 0.8, 0.0)
                self['text1_fg'] = (0, 1, 0.8, 1)
                self['text2_fg'] = (0.3, 1, 0.9, 1)
                self['text_pos'] = (0, 0.19)
                logoModel = loader.loadModel('phase_3/models/gui/members_only_gui')
                logo = DirectFrame(parent=self, relief=None, image=logoModel.find('**/MembersOnly'), image_scale=(0.4375,
                                                                                                                  0,
                                                                                                                  0.375), image_pos=(0,
                                                                                                                                     0,
                                                                                                                                     0))
            else:
                self['text0_scale'] = 0.1
                self['text1_scale'] = TTLocalizer.ACsubscribersOnly
                self['text2_scale'] = TTLocalizer.ACsubscribersOnly
                self['text0_fg'] = (0, 1, 0.8, 0.0)
                self['text1_fg'] = (0, 1, 0.8, 1)
                self['text2_fg'] = (0.3, 1, 0.9, 1)
                self['text_pos'] = (0, 0.19)
                upsellModel = loader.loadModel('phase_3/models/gui/tt_m_gui_ups_mainGui')
                upsellTex = upsellModel.find('**/tt_t_gui_ups_logo_noBubbles')
                self.logoModelImage = loader.loadModel('phase_3/models/gui/members_only_gui').find('**/MembersOnly')
                logo = DirectFrame(state=DGG.DISABLED, parent=self, relief=None, image=upsellTex, image_scale=(0.9,
                                                                                                               0,
                                                                                                               0.9), image_pos=(0,
                                                                                                                                0,
                                                                                                                                0), scale=0.45)
            logo.reparentTo(self.stateNodePath[0], 20)
            logo.instanceTo(self.stateNodePath[1], 20)
            logo.instanceTo(self.stateNodePath[2], 20)
            if config.GetBool('want-retro-mode', False):
                logoModel.removeNode()
            else:
                self.logo = logo
                upsellModel.removeNode()
        else:
            if self.mode is AvatarChoice.MODE_CREATE:
                self['command'] = self.__handleCreate
                if base.cr.isAprilFools:
                    self['text'] = (
                     TTLocalizer.AvatarChoiceMakeAToonAF,)
                    self['text_pos'] = (0, 0.05)
                else:
                    self['text'] = (
                     TTLocalizer.AvatarChoiceMakeAToon,)
                    self['text_pos'] = (0, 0)
                self['text0_scale'] = 0.1
                self['text1_scale'] = TTLocalizer.ACmakeAToon
                self['text2_scale'] = TTLocalizer.ACmakeAToon
                if base.cr.isHalloween:
                    if position in (1, 3, 5):
                        self['text0_fg'] = (0.4, 0, 0.8, 1)
                        self['text1_fg'] = (0.4, 0, 0.8, 1)
                        self['text2_fg'] = (0.4, 0, 0.8, 1)
                    else:
                        self['text0_fg'] = (0.8, 0.4, 0, 1)
                        self['text1_fg'] = (0.8, 0.4, 0, 1)
                        self['text2_fg'] = (0.8, 0.4, 0, 1)
                else:
                    self['text0_fg'] = (0, 1, 0.8, 0.5)
                    self['text1_fg'] = (0, 1, 0.8, 1)
                    self['text2_fg'] = (0.3, 1, 0.9, 1)
            else:
                self['command'] = self.__handleChoice
                if config.GetBool('want-retro-mode', False):
                    self['text'] = (
                     '', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
                    self['text_scale'] = 0.12
                    self['text_fg'] = (1, 0.9, 0.1, 1)
                    self.nameText = DirectLabel(parent=self, relief=None, scale=0.089, pos=(0,
                                                                                            0,
                                                                                            0.27), text=self.name, text_fg=(1,
                                                                                                                            1,
                                                                                                                            1,
                                                                                                                            1), text_shadow=(0,
                                                                                                                                             0,
                                                                                                                                             0,
                                                                                                                                             1), text_wordwrap=7.5, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                else:
                    if base.cr.isHalloween:
                        self['text'] = (
                         '', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
                        self['text_scale'] = TTLocalizer.ACplayThisToon
                        if position in (1, 3, 5):
                            self['text_fg'] = (0.4, 0, 0.8, 1)
                        else:
                            self['text_fg'] = (0.8, 0.4, 0, 1)
                        self['text_shadow'] = (0, 0, 0, 1)
                        if position in (1, 3, 5):
                            self.nameText = DirectLabel(parent=self, relief=None, scale=0.08, pos=NAME_POSITIONS[position], text=self.name, hpr=(0, 0, NAME_ROTATIONS[position]), text_fg=(0.4,
                                                                                                                                                                                           0,
                                                                                                                                                                                           0.8,
                                                                                                                                                                                           1), text_shadow=(0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                        else:
                            self.nameText = DirectLabel(parent=self, relief=None, scale=0.08, pos=NAME_POSITIONS[position], text=self.name, hpr=(0, 0, NAME_ROTATIONS[position]), text_fg=(0.8,
                                                                                                                                                                                           0.4,
                                                                                                                                                                                           0,
                                                                                                                                                                                           1), text_shadow=(0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                    else:
                        if base.cr.isWinter:
                            self['text'] = (
                             '', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
                            self['text_scale'] = TTLocalizer.ACplayThisToon
                            self['text_fg'] = (0.8, 0.1, 0.1, 1)
                            self['text_shadow'] = (0, 0, 0, 1)
                            self.nameText = DirectLabel(parent=self, relief=None, scale=0.08, pos=NAME_POSITIONS[position], text=self.name, hpr=(0, 0, NAME_ROTATIONS[position]), text_fg=(1,
                                                                                                                                                                                           1,
                                                                                                                                                                                           1,
                                                                                                                                                                                           1), text_shadow=(0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                        else:
                            self['text'] = (
                             '', TTLocalizer.AvatarChoicePlayThisToon, TTLocalizer.AvatarChoicePlayThisToon)
                            self['text_scale'] = TTLocalizer.ACplayThisToon
                            self['text_fg'] = (1, 0.9, 0.1, 1)
                            self.nameText = DirectLabel(parent=self, relief=None, scale=0.08, pos=NAME_POSITIONS[position], text=self.name, hpr=(0, 0, NAME_ROTATIONS[position]), text_fg=(1,
                                                                                                                                                                                           1,
                                                                                                                                                                                           1,
                                                                                                                                                                                           1), text_shadow=(0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            0,
                                                                                                                                                                                                            1), text_wordwrap=8, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                if self.approvedName != '':
                    self.nameText['text'] = self.approvedName
                guiButton = loader.loadModel('phase_3/models/gui/quit_button')
                self.nameYourToonButton = DirectButton(parent=self, relief=None, image=(guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR')), text=(TTLocalizer.AvatarChoiceNameYourToon, TTLocalizer.AvatarChoiceNameYourToon, TTLocalizer.AvatarChoiceNameYourToon), text_fg=(1,
                                                                                                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                                                                                                1), text_shadow=(0,
                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                 1), text_scale=0.15, text_pos=(0,
                                                                                                                                                                                                                                                                                                                                                                                0.03), text_font=ToontownGlobals.getInterfaceFont(), pos=(-0.2,
                                                                                                                                                                                                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                                                                                                                                                                                                          -0.3), scale=0.45, image_scale=(2,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                          1,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                          3), command=self.__handleNameYourToon)
                guiButton.removeNode()
                self.statusText = DirectLabel(parent=self, relief=None, scale=0.09, pos=(0,
                                                                                         0,
                                                                                         -0.24), text='', text_fg=(1,
                                                                                                                   1,
                                                                                                                   1,
                                                                                                                   1), text_shadow=(0,
                                                                                                                                    0,
                                                                                                                                    0,
                                                                                                                                    1), text_wordwrap=7.5, text_scale=TTLocalizer.ACstatusText, text_font=ToontownGlobals.getToonFont(), state=DGG.DISABLED)
                if self.wantName != '':
                    self.nameYourToonButton.hide()
                    self.statusText['text'] = TTLocalizer.AvatarChoiceNameReview
                else:
                    if self.approvedName != '':
                        self.nameYourToonButton.hide()
                        self.statusText['text'] = TTLocalizer.AvatarChoiceNameApproved
                    else:
                        if self.rejectedName != '':
                            self.nameYourToonButton.hide()
                            self.statusText['text'] = TTLocalizer.AvatarChoiceNameRejected
                        else:
                            if self.allowedName == 1 and (base.cr.allowFreeNames() or self.hasPaid):
                                self.nameYourToonButton.show()
                                self.statusText['text'] = ''
                            else:
                                self.nameYourToonButton.hide()
                                self.statusText['text'] = ''
                self.head = hidden.attachNewNode('head')
                self.head.setPosHprScale(0, 5, -0.1, 180, 0, 0, 0.24, 0.24, 0.24)
                self.head.reparentTo(self.stateNodePath[0], 20)
                self.head.instanceTo(self.stateNodePath[1], 20)
                self.head.instanceTo(self.stateNodePath[2], 20)
                self.headModel = ToonHead.ToonHead()
                self.headModel.setupHead(self.dna, forGui=1)
                self.headModel.reparentTo(self.head)
                animalStyle = self.dna.getAnimal()
                bodyScale = ToontownGlobals.toonBodyScales[animalStyle]
                self.headModel.setScale(bodyScale / 0.75)
                self.headModel.startBlink()
                self.headModel.startLookAround()
                if base.cr.isHalloween:
                    trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui_halloween')
                else:
                    trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
                if config.GetBool('want-retro-mode', False):
                    self.deleteButton = DirectButton(parent=self, image=(
                     trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'),
                     trashcanGui.find('**/TrashCan_RLVR')), text=(
                     '', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1,
                                                                                                   1,
                                                                                                   1,
                                                                                                   1), text_shadow=(0,
                                                                                                                    0,
                                                                                                                    0,
                                                                                                                    1), text_scale=0.15, text_pos=(0,
                                                                                                                                                   -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=(0.27,
                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                          -0.25), scale=0.45, command=self.__handleDelete)
                else:
                    self.deleteButton = DirectButton(parent=self, image=(trashcanGui.find('**/TrashCan_CLSD'), trashcanGui.find('**/TrashCan_OPEN'), trashcanGui.find('**/TrashCan_RLVR')), text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete), text_fg=(1,
                                                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                                                1,
                                                                                                                                                                                                                                                                                1), text_shadow=(0,
                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                 1), text_scale=0.15, text_pos=(0,
                                                                                                                                                                                                                                                                                                                                -0.1), text_font=ToontownGlobals.getInterfaceFont(), relief=None, pos=DELETE_POSITIONS[position], scale=0.45, command=self.__handleDelete)
                trashcanGui.removeNode()
        self.resetFrameSize()
        self.avForLogging = None
        if av:
            self.avForLogging = str(av.id)
        else:
            self.avForLogging = None
        return

    def destroy(self):
        loader.unloadModel('phase_3/models/gui/pick_a_toon_gui')
        self.pickAToonGui.removeNode()
        del self.pickAToonGui
        del self.dna
        if self.mode in (AvatarChoice.MODE_CREATE, AvatarChoice.MODE_LOCKED):
            pass
        else:
            self.headModel.stopBlink()
            self.headModel.stopLookAroundNow()
            self.headModel.delete()
            self.head.removeNode()
            del self.head
            del self.headModel
            del self.nameText
            del self.statusText
            self.deleteButton.destroy()
            del self.deleteButton
            self.nameYourToonButton.destroy()
            del self.nameYourToonButton
            loader.unloadModel('phase_3/models/gui/trashcan_gui')
            loader.unloadModel('phase_3/models/gui/quit_button')
        DirectFrame.destroy(self)
        if self.deleteWithPasswordFrame:
            self.deleteWithPasswordFrame.destroy()

    def __handleChoice(self):
        cleanupDialog('globalDialog')
        messenger.send(self.doneEvent, ['chose', self.position])

    def __handleCreate(self):
        cleanupDialog('globalDialog')
        messenger.send(self.doneEvent, ['create', self.position])

    def __handleDelete(self):
        cleanupDialog('globalDialog')
        self.verify = TTDialog.TTGlobalDialog(doneEvent='verifyDone', message=TTLocalizer.AvatarChoiceDeleteConfirm % self.name, style=TTDialog.TwoChoice)
        self.verify.show()
        self.accept('verifyDone', self.__handleVerifyDelete)

    def __handleNameYourToon(self):
        messenger.send(self.doneEvent, ['nameIt', self.position])

    def __handleVerifyDelete(self):
        status = self.verify.doneStatus
        self.ignore('verifyDone')
        self.verify.cleanup()
        del self.verify
        if status == 'ok':
            self.verifyDeleteWithPassword()

    def verifyDeleteWithPassword(self):
        if base.cr.isAprilFools:
            deleteText = TTLocalizer.AvatarChoiceDeleteConfirmTextAF
        else:
            deleteText = TTLocalizer.AvatarChoiceDeleteConfirmText % {'name': self.name, 
               'confirm': TTLocalizer.AvatarChoiceDeleteConfirmUserTypes}
        if self.deleteWithPasswordFrame == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
            self.deleteWithPasswordFrame = DirectFrame(pos=(0.0, 0.1, 0.2), parent=aspect2dp, relief=None, image=DGG.getDefaultDialogGeom(), image_color=ToontownGlobals.GlobalDialogColor, image_scale=(1.4,
                                                                                                                                                                                                         1.0,
                                                                                                                                                                                                         1.0), text=deleteText, text_wordwrap=19, text_scale=TTLocalizer.ACdeleteWithPasswordFrame, text_pos=(0,
                                                                                                                                                                                                                                                                                                              0.25), textMayChange=1, sortOrder=DGG.NO_FADE_SORT_INDEX)
            self.deleteWithPasswordFrame.hide()
            self.passwordEntry = DirectEntry(parent=self.deleteWithPasswordFrame, relief=None, image=nameBalloon, image1_color=(0.8,
                                                                                                                                0.8,
                                                                                                                                0.8,
                                                                                                                                1.0), scale=0.064, pos=(-0.3,
                                                                                                                                                        0.0,
                                                                                                                                                        -0.2), width=10, numLines=1, focus=1, cursorKeys=1, command=self.__handleDeleteWithConfirmOK)
            DirectButton(parent=self.deleteWithPasswordFrame, image=okButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordOK, text_scale=0.05, text_pos=(0.0,
                                                                                                                                                                          -0.1), textMayChange=0, pos=(-0.22,
                                                                                                                                                                                                       0.0,
                                                                                                                                                                                                       -0.35), command=self.__handleDeleteWithConfirmOK)
            if base.cr.isAprilFools:
                DirectLabel(parent=self.deleteWithPasswordFrame, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.35), text=TTLocalizer.AvatarChoiceDeletePasswordTitleAF, textMayChange=0, text_scale=0.08)
            else:
                DirectLabel(parent=self.deleteWithPasswordFrame, relief=None, pos=(0,
                                                                                   0,
                                                                                   0.35), text=TTLocalizer.AvatarChoiceDeletePasswordTitle, textMayChange=0, text_scale=0.08)
            DirectButton(parent=self.deleteWithPasswordFrame, image=cancelButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordCancel, text_scale=0.05, text_pos=(0.0,
                                                                                                                                                                                  -0.1), textMayChange=1, pos=(0.2,
                                                                                                                                                                                                               0.0,
                                                                                                                                                                                                               -0.35), command=self.__handleDeleteWithPasswordCancel)
            buttons.removeNode()
            nameBalloon.removeNode()
        else:
            self.deleteWithPasswordFrame['text'] = deleteText
            self.passwordEntry['focus'] = 1
            self.passwordEntry.enterText('')
        base.transitions.fadeScreen(0.5)
        self.deleteWithPasswordFrame.show()
        return

    def __handleDeleteWithConfirmOK(self, *args):
        password = self.passwordEntry.get()
        passwordMatch = TTLocalizer.AvatarChoiceDeleteConfirmUserTypes
        password = TextEncoder.lower(password)
        passwordMatch = TextEncoder.lower(passwordMatch)
        if password == passwordMatch:
            self.deleteWithPasswordFrame.hide()
            base.transitions.noTransitions()
            messenger.send(self.doneEvent, ['delete', self.position])
            if config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: DELETEATOON: Deleting A Toon')
        else:
            self.deleteWithPasswordFrame['text'] = TTLocalizer.AvatarChoiceDeleteWrongConfirm % {'name': self.name, 'confirm': TTLocalizer.AvatarChoiceDeleteConfirmUserTypes}
            self.passwordEntry['focus'] = 1
            self.passwordEntry.enterText('')

    def __handleDeleteWithPasswordCancel(self):
        self.deleteWithPasswordFrame.hide()
        base.transitions.noTransitions()

    def __handleTrialer(self):
        TeaserPanel.TeaserPanel(pageName='sixToons')