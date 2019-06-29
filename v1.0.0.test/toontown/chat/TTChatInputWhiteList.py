from otp.chat.ChatInputWhiteListFrame import ChatInputWhiteListFrame
from toontown.chat.TTWhiteList import TTWhiteList
from direct.showbase import DirectObject
from otp.otpbase import OTPGlobals
import sys
from direct.gui.DirectGui import *
from panda3d.core import *
from otp.otpbase import OTPLocalizer
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals

class TTChatInputWhiteList(ChatInputWhiteListFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTChatInputWhiteList')
    TFToggleKey = base.config.GetString('true-friend-toggle-key', 'alt')
    TFToggleKeyUp = TFToggleKey + '-up'

    def __init__(self, parent=None, **kw):
        entryOptions = {'parent': self, 'relief': DGG.SUNKEN, 
           'scale': 0.05, 
           'frameColor': (0.9, 0.9, 0.85, 0.0), 
           'pos': (-0.195, 0, 0.1), 
           'entryFont': OTPGlobals.getInterfaceFont(), 
           'width': 10.2, 
           'numLines': 8, 
           'cursorKeys': 0, 
           'backgroundFocus': 0, 
           'suppressKeys': 0, 
           'suppressMouse': 1, 
           'command': self.sendChat, 
           'failedCommand': self.sendFailed, 
           'focus': 0, 
           'text': '', 
           'sortOrder': DGG.FOREGROUND_SORT_INDEX}
        ChatInputWhiteListFrame.__init__(self, entryOptions, parent, **kw)
        self.whiteList = TTWhiteList()
        base.whiteList = self.whiteList
        base.ttwl = self
        self.autoOff = 1
        self.sendBy = 'Data'
        self.prefilter = 0
        self.promoteWhiteList = 1
        self.typeGrabbed = 0
        self.globalState = 0
        self.deactivate()
        gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui')
        self.chatFrame = DirectFrame(parent=self, image=gui.find('**/Chat_Bx_FNL'), relief=None, pos=(0.05,
                                                                                                      0,
                                                                                                      -0.1), state=DGG.NORMAL, scale=(1.1,
                                                                                                                                      1.1,
                                                                                                                                      0.9))
        self.chatButton = DirectButton(parent=self.chatFrame, image=(gui.find('**/ChtBx_ChtBtn_UP'),
         gui.find('**/ChtBx_ChtBtn_DN'),
         gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.172, 0, -0.228), scale=(1.1, 1.1,
                                                                           1.3), relief=None, text=(
         '', OTPLocalizer.ChatInputNormalSayIt, OTPLocalizer.ChatInputNormalSayIt), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0,
                                                                                                                                                                       -0.09), textMayChange=0, command=self.chatButtonPressed)
        self.cancelButton = DirectButton(parent=self.chatFrame, image=(gui.find('**/CloseBtn_UP'),
         gui.find('**/CloseBtn_DN'),
         gui.find('**/CloseBtn_Rllvr')), pos=(-0.171, 0, -0.228), scale=(1.1, 1.1,
                                                                         1.3), relief=None, text=(
         '', OTPLocalizer.ChatInputNormalCancel,
         OTPLocalizer.ChatInputNormalCancel), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0,
                                                                                                                                 -0.09), textMayChange=0, command=self.cancelButtonPressed)
        self.globalButton = DirectButton(parent=self.chatFrame, image=(gui.find('**/ChtBx_GlbBtn_RLVR'),
         gui.find('**/ChtBx_GlbBtn_UP'),
         gui.find('**/ChtBx_GlbBtn_DN')), pos=(0.0025, 0, -0.228), scale=(1.1, 1.1,
                                                                          1.3), relief=None, text=(
         '', OTPLocalizer.ChatInputNormalGlobal), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0,
                                                                                                                                     -0.09), textMayChange=0, command=self.globalButtonPressed)
        gui.removeNode()
        self.whisperLabel = DirectLabel(parent=self.chatFrame, pos=(0.01, 0, 0.36), relief=DGG.FLAT, frameColor=(1,
                                                                                                                 1,
                                                                                                                 0.5,
                                                                                                                 1), frameSize=(-0.23,
                                                                                                                                0.23,
                                                                                                                                -0.07,
                                                                                                                                0.05), text=OTPLocalizer.ChatInputNormalWhisper, text_scale=0.05, text_pos=(0,
                                                                                                                                                                                                            -0.025,
                                                                                                                                                                                                            0), text_fg=Vec4(0, 0, 0, 1), text_wordwrap=9.5, textMayChange=1)
        self.chatEntry.bind(DGG.OVERFLOW, self.chatOverflow)
        self.chatEntry.bind(DGG.TYPE, self.typeCallback)
        self.trueFriendChat = 0
        if base.config.GetBool('whisper-to-nearby-true-friends', 1):
            self.accept(self.TFToggleKey, self.shiftPressed)
        return

    def shiftPressed(self):
        self.ignore(self.TFToggleKey)
        self.trueFriendChat = 1
        self.accept(self.TFToggleKeyUp, self.shiftReleased)

    def shiftReleased(self):
        self.ignore(self.TFToggleKeyUp)
        self.trueFriendChat = 0
        self.accept(self.TFToggleKey, self.shiftPressed)

    def handleTypeGrab(self):
        self.ignore('typeEntryGrab')
        self.accept('typeEntryRelease', self.handleTypeRelease)
        self.typeGrabbed = 1

    def handleTypeRelease(self):
        self.ignore('typeEntryRelease')
        self.accept('typeEntryGrab', self.handleTypeGrab)
        self.typeGrabbed = 0

    def typeCallback(self, extraArgs):
        if len(self.chatEntry.get(plain=True)) > OTPGlobals.MaxChatLength:
            self.chatOverflow(self.chatEntry.get(plain=True))
            return
        if self.typeGrabbed:
            return
        self.applyFilter(extraArgs)
        if localAvatar.chatMgr.chatInputWhiteList.isActive():
            return
        messenger.send('wakeup')
        messenger.send('enterNormalChat')

    def destroy(self):
        self.chatEntry.destroy()
        self.chatFrame.destroy()
        self.ignoreAll()
        ChatInputWhiteListFrame.destroy(self)

    def delete(self):
        base.whiteList = None
        ChatInputWhiteListFrame.delete(self)
        return

    def sendChat(self, text, overflow=False):
        if self.typeGrabbed:
            return
        state = self.getCurrentOrNextState()
        if state == 'Off':
            base.localAvatar.chatMgr.chatLog.openChatlog()
        ChatInputWhiteListFrame.sendChat(self, self.chatEntry.get())

    def sendChatByData(self, text):
        if self.trueFriendChat:
            for friendId, flags in base.localAvatar.friendsList:
                if flags & ToontownGlobals.FriendChat:
                    self.sendWhisperByFriend(friendId, text)

        else:
            if self.globalState:
                base.talkAssistant.sendGlobalTalk(text)
            else:
                if not self.receiverId:
                    base.talkAssistant.sendOpenTalk(text)
                else:
                    if self.receiverId and not self.toPlayer:
                        base.talkAssistant.sendWhisperTalk(text, self.receiverId)
                    else:
                        if self.receiverId and self.toPlayer:
                            base.talkAssistant.sendAccountTalk(text, self.receiverId)

    def sendWhisperByFriend(self, avatarId, text):
        online = 0
        if avatarId in base.cr.doId2do:
            online = 1
        avatarUnderstandable = 0
        av = None
        if avatarId:
            av = base.cr.identifyAvatar(avatarId)
        if av != None:
            avatarUnderstandable = av.isUnderstandable()
        if avatarUnderstandable and online:
            base.talkAssistant.sendWhisperTalk(text, avatarId)
        return

    def chatButtonPressed(self):
        if self.okayToSubmit:
            self.sendChat(self.chatEntry.get())
        else:
            self.sendFailed(self.chatEntry.get())

    def cancelButtonPressed(self):
        self.requestMode('Off')
        localAvatar.chatMgr.fsm.request('mainMenu')

    def enterAllChat(self):
        ChatInputWhiteListFrame.enterAllChat(self)
        self.whisperLabel.hide()

    def exitAllChat(self):
        ChatInputWhiteListFrame.exitAllChat(self)

    def enterPlayerWhisper(self):
        ChatInputWhiteListFrame.enterPlayerWhisper(self)
        self.labelWhisper()

    def exitPlayerWhisper(self):
        ChatInputWhiteListFrame.exitPlayerWhisper(self)
        self.whisperLabel.hide()

    def enterAvatarWhisper(self):
        ChatInputWhiteListFrame.enterAvatarWhisper(self)
        self.globalButton.component('text3').hide()
        self.globalButton['state'] = DGG.DISABLED
        self.labelWhisper()

    def exitAvatarWhisper(self):
        ChatInputWhiteListFrame.exitAvatarWhisper(self)
        self.globalButton['state'] = DGG.NORMAL
        self.globalButton.component('text3').show()
        self.whisperLabel.hide()

    def labelWhisper(self):
        if self.receiverId:
            self.whisperName = base.talkAssistant.findName(self.receiverId, self.toPlayer)
            self.whisperLabel['text'] = OTPLocalizer.ChatInputWhisperLabel % self.whisperName
            self.whisperLabel.show()
        else:
            self.whisperLabel.hide()

    def applyFilter(self, keyArgs, strict=False):
        text = self.chatEntry.get(plain=True)
        activators = []
        activators.append(base.cr.magicWordManager.chatPrefix)
        if config.GetBool('exec-chat', 0):
            activators.append('>')
        if len(text) > 0 and text[0] in activators:
            self.okayToSubmit = True
        else:
            words = text.split(' ')
            newwords = []
            self.okayToSubmit = True
            flag = 0
            for friendId, flags in base.localAvatar.friendsList:
                if flags & ToontownGlobals.FriendChat:
                    flag = 1

            for word in words:
                if word == '' or self.whiteList.isWord(word) or not base.cr.whiteListChatEnabled:
                    newwords.append(word)
                else:
                    if self.checkBeforeSend:
                        self.okayToSubmit = False
                    else:
                        self.okayToSubmit = True
                    if flag:
                        newwords.append('\x01WLDisplay\x01' + word + '\x02')
                    else:
                        newwords.append('\x01WLEnter\x01' + word + '\x02')

            if not strict:
                lastword = words[(-1)]
                if lastword == '' or self.whiteList.isPrefix(lastword) or not base.cr.whiteListChatEnabled:
                    newwords[-1] = lastword
                elif flag:
                    newwords[-1] = '\x01WLDisplay\x01' + lastword + '\x02'
                else:
                    newwords[-1] = '\x01WLEnter\x01' + lastword + '\x02'
            newtext = (' ').join(newwords)
            self.chatEntry.set(newtext)
        self.chatEntry.guiItem.setAcceptEnabled(self.okayToSubmit)

    def globalButtonPressed(self, force=False):
        gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui')
        globalState = self.globalState
        if force:
            globalState = 1
        if not globalState:
            self.globalState = 1
            self.globalButton['image'] = gui.find('**/ChtBx_GlbBtn_UP')
        else:
            if globalState:
                self.globalState = 0
                self.globalButton['image'] = (gui.find('**/ChtBx_GlbBtn_RLVR'),
                 gui.find('**/ChtBx_GlbBtn_UP'),
                 gui.find('**/ChtBx_GlbBtn_DN'))
        gui.removeNode()