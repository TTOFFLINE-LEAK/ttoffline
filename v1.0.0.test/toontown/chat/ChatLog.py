from panda3d.core import *
from direct.gui.DirectGui import *
from otp.otpbase import OTPLocalizer, OTPGlobals
from toontown.shtiker.OptionsPage import speedChatStyles
from toontown.toonbase import ToontownGlobals, TTLocalizer
from libotp.nametag import NametagGlobals
from direct.task import Task
from otp.speedchat.ColorSpace import *
from direct.showbase.PythonUtil import makeTuple
from libotp import WhisperPopup
import re

class ChatLog(DirectButton):

    def __init__(self, **kwargs):
        gui = loader.loadModel('phase_3/models/gui/ChatPanel')

        def findNodes(names, model=gui):
            results = []
            for name in names:
                for nm in makeTuple(name):
                    node = model.find('**/%s' % nm)
                    if not node.isEmpty():
                        results.append(node)
                        break

            return results

        def scaleNodes(nodes, scale):
            bgTop, bgBottom, bgLeft, bgRight, bgMiddle, bgTopLeft, bgBottomLeft, bgTopRight, bgBottomRight = nodes
            bgTopLeft.setSx(aspect2d, scale)
            bgTopLeft.setSz(aspect2d, scale)
            bgBottomRight.setSx(aspect2d, scale)
            bgBottomRight.setSz(aspect2d, scale)
            bgBottomLeft.setSx(aspect2d, scale)
            bgBottomLeft.setSz(aspect2d, scale)
            bgTopRight.setSx(aspect2d, scale)
            bgTopRight.setSz(aspect2d, scale)
            bgTop.setSz(aspect2d, scale)
            bgBottom.setSz(aspect2d, scale)
            bgLeft.setSx(aspect2d, scale)
            bgRight.setSx(aspect2d, scale)

        nodes = findNodes([('top', 'top1'), 'bottom', 'left', 'right', 'middle', 'topLeft', 'bottomLeft', 'topRight',
         'bottomRight'])
        scaleNodes(nodes, 0.25)
        pos = base.settings.getOption('game', 'chat-log-pos', [-1.83087, 0, 1.28859])
        args = {'parent': base.a2dBottomCenter, 'relief': None, 'geom': gui, 'geom_scale': (1, 1, 0.55), 'pos': (
                 pos[0], pos[1], pos[2])}
        kwargs.update(args)
        DirectButton.__init__(self, **kwargs)
        self.initialiseoptions(ChatLog)
        self['geom'].setBin('fixed', 0)
        scaleNodes(nodes, 0.45)
        buttonRowOffset = 0.225
        self.currentTab = 0
        self.chatTabs = []
        mainTab = DirectButton(parent=self, relief=None, geom=gui, geom_scale=(1.2,
                                                                               1,
                                                                               0.55), text='Main', text_scale=0.25, text_pos=(0.6,
                                                                                                                              -0.3,
                                                                                                                              0.0), scale=0.15, pos=(0.0,
                                                                                                                                                     0.0,
                                                                                                                                                     0.09), command=self.__toggleButton, extraArgs=[0])
        whisperTab = DirectButton(parent=self, relief=None, geom=gui, geom_scale=(1.2,
                                                                                  1,
                                                                                  0.55), text='Whispers', text_scale=0.25, text_pos=(0.6,
                                                                                                                                     -0.3,
                                                                                                                                     0.0), text_fg=(0,
                                                                                                                                                    0,
                                                                                                                                                    0,
                                                                                                                                                    0.5), scale=0.15, pos=(
         buttonRowOffset, 0.0, 0.09), command=self.__toggleButton, extraArgs=[1])
        globalTab = DirectButton(parent=self, relief=None, geom=gui, geom_scale=(1.2,
                                                                                 1,
                                                                                 0.55), text='Global', text_scale=0.25, text_pos=(0.6,
                                                                                                                                  -0.3,
                                                                                                                                  0.0), text_fg=(0,
                                                                                                                                                 0,
                                                                                                                                                 0,
                                                                                                                                                 0.5), scale=0.15, pos=(
         buttonRowOffset * 2, 0.0, 0.09), command=self.__toggleButton, extraArgs=[2])
        systemTab = DirectButton(parent=self, relief=None, geom=gui, geom_scale=(1.2,
                                                                                 1,
                                                                                 0.55), text='System', text_scale=0.25, text_pos=(0.6,
                                                                                                                                  -0.3,
                                                                                                                                  0.0), text_fg=(0,
                                                                                                                                                 0,
                                                                                                                                                 0,
                                                                                                                                                 0.5), scale=0.15, pos=(
         buttonRowOffset * 3, 0.0, 0.09), command=self.__toggleButton, extraArgs=[3])
        self.exitTab = DirectButton(parent=self, relief=None, geom=gui, geom_scale=(0.55,
                                                                                    1,
                                                                                    0.55), text='X', text_scale=0.4, text_pos=(0.26,
                                                                                                                               -0.35,
                                                                                                                               0.0), text_fg=(1,
                                                                                                                                              0,
                                                                                                                                              0,
                                                                                                                                              0.5), scale=0.15, pos=(
         buttonRowOffset * 4.1, 0.0, 0.09), command=self.closeChatlog)
        self.chatTabs.append(mainTab)
        self.chatTabs.append(whisperTab)
        self.chatTabs.append(globalTab)
        self.chatTabs.append(systemTab)
        gui.removeNode()
        self.logs = []
        self.realLogs = []
        self.currents = []
        self.texts = []
        self.textNodes = []
        for x in range(len(self.chatTabs)):
            log = []
            realLog = []
            current = 0
            text = TextNode('text')
            text.setWordwrap(23.5)
            text.setAlign(TextNode.ALeft)
            text.setTextColor(0, 0, 0, 1)
            text.setFont(ToontownGlobals.getToonFont())
            textNode = self.attachNewNode(text, 0)
            textNode.setPos(0.0, 0.0, -0.05)
            textNode.setScale(0.04)
            self.logs.append(log)
            self.realLogs.append(realLog)
            self.currents.append(current)
            self.texts.append(text)
            self.textNodes.append(textNode)

        self.autoScroll = True
        self.closed = False
        self.bind(DGG.B1PRESS, self.dragStart)
        self.bind(DGG.B1RELEASE, self.dragStop)
        self.accept('addChatHistory', self.__addChatHistory)
        self.accept('SpeedChatStyleChange', self.__updateSpeedChatStyle)
        self.__toggleButton(0)
        if not config.GetBool('chat-log-open', False):
            self.closeChatlog()
        return

    def destroy(self):
        if not hasattr(self, 'logs'):
            return
        for log in self.logs:
            del log

        for text in self.texts:
            del text

        for textNode in self.textNodes:
            textNode.removeNode()
            del textNode

        taskMgr.remove(self.taskName('dragTask'))
        DirectButton.destroy(self)
        self.ignoreAll()

    def show(self):
        if self.closed:
            return
        DirectButton.show(self)
        self.__updateSpeedChatStyle()
        self.computeRealLog(0)
        base.settings.updateSetting('game', 'chat-log-open', True)
        self.accept('wheel_up-up', self.__wheel, [-1])
        self.accept('wheel_down-up', self.__wheel, [1])

    def hide(self):
        DirectButton.hide(self)
        base.settings.updateSetting('game', 'chat-log-open', False)
        self.ignore('wheel_up-up')
        self.ignore('wheel_down-up')

    def closeChatlog(self):
        self.closed = True
        self.hide()

    def openChatlog(self):
        if not self.closed:
            return
        self.closed = False
        self.show()

    def scrollToCurrent(self, tab):
        minimum = max(0, self.currents[tab] - 12)
        self.texts[tab].setText(('\n').join(self.realLogs[tab][minimum:self.currents[tab]]))

    def computeRealLog(self, tab):
        oldText = self.texts[tab].getText()
        self.texts[tab].setText(('\n').join(self.logs[tab]))
        self.realLogs[tab] = self.texts[tab].getWordwrappedText().split('\n')
        if self.autoScroll:
            self.currents[tab] = len(self.realLogs[tab])
            self.scrollToCurrent(tab)
        else:
            self.texts[tab].setText(oldText)

    def __updateSpeedChatStyle(self):
        color = speedChatStyles[base.localAvatar.speedChatStyleIndex][3]
        h, s, v = rgb2hsv(*color)
        color = hsv2rgb(h, 0.5 * s, v)
        r, g, b = color
        self['geom_color'] = (r, g, b, 0.9)
        for tab in self.chatTabs:
            tab['geom_color'] = (
             r, g, b, 0.9)

        self.exitTab['geom_color'] = (
         r, g, b, 0.9)

    def __exit(self):
        base.localAvatar.chatMgr.fsm.request('mainMenu')

    def __addChatHistory(self, name, font, speechFont, color, chat, type=WhisperPopup.WTNormal):
        tab = 0
        colon = ':'
        if name and not font and not speechFont:
            tab = 1
        if not speechFont:
            speechFont = OTPGlobals.getInterfaceFont()
        if font == ToontownGlobals.getSuitFont():
            color = 5
        if not name:
            if ':' in chat:
                name, chat = chat.split(':', 1)
            else:
                name = 'System'
        if not font:
            font = OTPGlobals.getInterfaceFont()
        if isinstance(color, int):
            color = NametagGlobals.getArrowColor(color)
        if type in (WhisperPopup.WTSystem, WhisperPopup.WTMagicWord):
            tab = 3
        else:
            if type == WhisperPopup.WTGlobal:
                tab = 2
            else:
                if type == WhisperPopup.WTQuickTalker:
                    tab = 1
                    if name == base.localAvatar.getName():
                        name = OTPLocalizer.MeToReceiver % name
                    else:
                        name = OTPLocalizer.ReceiverToMe % name
            self.logs[tab].append('\x01%s\x01\x01%s\x01%s%s\x02\x02 \x01%s\x01%s\x02' % (OTPLocalizer.getPropertiesForFont(font),
             OTPLocalizer.getPropertiesForColor(color),
             name, colon, OTPLocalizer.getPropertiesForFont(speechFont),
             chat))
            while len(self.logs[tab]) > 250:
                del self.logs[tab][0]

        if not self.isHidden():
            self.computeRealLog(tab)

    def __wheel(self, amount):
        oldCurrent = self.currents[self.currentTab]
        minimum = min(12, len(self.realLogs[self.currentTab]))
        self.currents[self.currentTab] += amount
        self.autoScroll = self.currents[self.currentTab] >= len(self.realLogs[self.currentTab])
        if self.autoScroll:
            self.currents[self.currentTab] = len(self.realLogs[self.currentTab])
        if self.currents[self.currentTab] < minimum:
            self.currents[self.currentTab] = minimum
        if oldCurrent != self.currents[self.currentTab]:
            self.scrollToCurrent(self.currentTab)

    def dragStart(self, event):
        taskMgr.remove(self.taskName('dragTask'))
        vWidget2render2d = self.getPos(render2d)
        vMouse2render2d = Point3(event.getMouse()[0], 0, event.getMouse()[1])
        editVec = Vec3(vWidget2render2d - vMouse2render2d)
        task = taskMgr.add(self.dragTask, self.taskName('dragTask'))
        task.editVec = editVec

    def dragTask(self, task):
        mwn = base.mouseWatcherNode
        if mwn.hasMouse():
            vMouse2render2d = Point3(mwn.getMouse()[0], 0, mwn.getMouse()[1])
            newPos = vMouse2render2d + task.editVec
            self.setPos(render2d, newPos)
        return Task.cont

    def dragStop(self, event):
        taskMgr.remove(self.taskName('dragTask'))
        messenger.send('PlayingCardDrop', sentArgs=[self])
        pos = self.getPos(base.a2dBottomCenter)
        print pos
        base.settings.updateSetting('game', 'chat-log-pos', (pos[0], pos[1], pos[2]))

    def __toggleButton(self, index):
        self.currentTab = index
        for x in range(len(self.chatTabs)):
            self.chatTabs[x]['text_fg'] = (0, 0, 0, 0.5)
            self.textNodes[x].hide()

        self.chatTabs[index]['text_fg'] = (0, 0, 0, 1)
        self.textNodes[index].show()