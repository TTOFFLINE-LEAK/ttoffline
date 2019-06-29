from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals, TTLocalizer

class PasswordScreen:
    notify = DirectNotifyGlobal.directNotify.newCategory('PasswordScreen')

    def __init__(self):
        self.passwordFrame = None
        self.passwordEntry = None
        return

    def load(self):
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
        okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
        self.passwordFrame = DirectFrame(pos=(0.0, 0.0, 0.0), parent=aspect2dp, relief=None, image=DGG.getDefaultDialogGeom(), image_color=ToontownGlobals.GlobalDialogColor, image_scale=(1.4,
                                                                                                                                                                                           1.0,
                                                                                                                                                                                           0.8), text=TTLocalizer.PasswordScreenDescription, text_wordwrap=19, text_scale=TTLocalizer.ACdeleteWithPasswordFrame, text_pos=(0,
                                                                                                                                                                                                                                                                                                                           0.15), textMayChange=1, sortOrder=DGG.NO_FADE_SORT_INDEX)
        self.passwordFrame.hide()
        self.passwordEntry = DirectEntry(parent=self.passwordFrame, relief=None, image=nameBalloon, image1_color=(0.8,
                                                                                                                  0.8,
                                                                                                                  0.8,
                                                                                                                  1.0), image_pos=(0.0,
                                                                                                                                   0.0,
                                                                                                                                   -0.45), scale=0.064, pos=(-0.3,
                                                                                                                                                             0.0,
                                                                                                                                                             -0.065), width=ToontownGlobals.maxLoginWidth, numLines=2, focus=1, cursorKeys=1, obscured=1, command=self.__handleOK)
        DirectButton(parent=self.passwordFrame, image=okButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordOK, text_scale=0.05, text_pos=(0.0,
                                                                                                                                                            -0.1), textMayChange=0, pos=(-0.22,
                                                                                                                                                                                         0.0,
                                                                                                                                                                                         -0.25), command=self.__handleOK)
        DirectLabel(parent=self.passwordFrame, relief=None, pos=(0, 0, 0.25), text=TTLocalizer.PasswordScreenTitle, textMayChange=0, text_scale=0.08)
        DirectButton(parent=self.passwordFrame, image=cancelButtonImage, relief=None, text=TTLocalizer.AvatarChoiceDeletePasswordCancel, text_scale=0.05, text_pos=(0.0,
                                                                                                                                                                    -0.1), textMayChange=1, pos=(0.2,
                                                                                                                                                                                                 0.0,
                                                                                                                                                                                                 -0.25), command=self.__handleCancel)
        buttons.removeNode()
        nameBalloon.removeNode()
        self.passwordFrame.show()
        return

    def __handleOK(self, *args):
        password = self.passwordEntry.get()
        playToken = base.cr.playToken or 'dev'
        base.accept('authenticatePasswordResponse', self.__handleAuthenticatePasswordResponse)
        messenger.send('authenticatePassword', [playToken, password])

    def __handleAuthenticatePasswordResponse(self, state):
        if state:
            base.cr.waitForDatabaseTimeout(requestName='WaitForGSMLoginResponse')
        else:
            self.passwordFrame['text'] = TTLocalizer.PasswordScreenIncorrectPassword
            self.passwordEntry['focus'] = 1
            self.passwordEntry.enterText('')

    def __handleCancel(self):
        cleanupDialog('globalDialog')
        base.cr.loginFSM.request('shutdown')

    def exit(self):
        if self.passwordFrame:
            self.passwordFrame.hide()
        if self.passwordEntry:
            self.passwordEntry.hide()

    def unload(self):
        if self.passwordFrame:
            self.passwordFrame.removeNode()
            self.passwordFrame = None
        if self.passwordEntry:
            self.passwordEntry.removeNode()
            self.passwordEntry = None
        return