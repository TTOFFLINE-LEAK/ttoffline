import json, urllib2, webbrowser
from collections import OrderedDict
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.task.Task import Task
from panda3d.core import *
import ShtikerPage
from otp.otpbase import PythonUtil
from toontown.distributed import ToontownDistrictStats
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog
POP_COLORS_NTT = (
 Vec4(0.0, 1.0, 0.0, 1.0), Vec4(1.0, 1.0, 0.0, 1.0), Vec4(1.0, 0.0, 0.0, 1.0))
POP_COLORS = (Vec4(0.4, 0.4, 1.0, 1.0), Vec4(0.4, 1.0, 0.4, 1.0), Vec4(1.0, 0.4, 0.4, 1.0))
PageMode = PythonUtil.Enum('Current, List')

class ServerPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('ServerPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.currentTabPage = CurrentTabPage(self, _parent=self)
        self.currentTabPage.hide()
        self.serverTabPage = ServerTabPage(self, _parent=self)
        self.serverTabPage.hide()
        titleHeight = 0.61
        self.serverTitle = ''
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.ServerPageTitle, text_scale=0.12, pos=(
         0, 0, titleHeight))
        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        diabledColor = (1.0, 0.98, 0.15, 1)
        gui = loader.loadModel('phase_3.5/models/gui/fishingBook')
        self.currentTab = DirectButton(parent=self, relief=None, text=TTLocalizer.ShardTabTitle, text_scale=TTLocalizer.OPoptionsTab, text_align=TextNode.ALeft, text_pos=(0.01,
                                                                                                                                                                           0.0,
                                                                                                                                                                           0.0), image=gui.find('**/tabs/polySurface1'), image_pos=(0.55,
                                                                                                                                                                                                                                    1,
                                                                                                                                                                                                                                    -0.91), image_hpr=(0,
                                                                                                                                                                                                                                                       0,
                                                                                                                                                                                                                                                       -90), image_scale=(0.033,
                                                                                                                                                                                                                                                                          0.033,
                                                                                                                                                                                                                                                                          0.035), image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor, image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode, extraArgs=[PageMode.Current], pos=(-0.36,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  0.77))
        self.serverTab = DirectButton(parent=self, relief=None, text=TTLocalizer.ServerPageTitle, text_scale=0.06, text_align=TextNode.ALeft, text_pos=(-0.035,
                                                                                                                                                        0.0,
                                                                                                                                                        0.0), image=gui.find('**/tabs/polySurface2'), image_pos=(0.12,
                                                                                                                                                                                                                 1,
                                                                                                                                                                                                                 -0.91), image_hpr=(0,
                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                    -90), image_scale=(0.033,
                                                                                                                                                                                                                                                       0.033,
                                                                                                                                                                                                                                                       0.035), image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor, image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode, extraArgs=[PageMode.List], pos=(0.11,
                                                                                                                                                                                                                                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                            0.77))
        return

    def enter(self):
        self.setMode(PageMode.Current, updateAnyways=1)
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.currentTabPage.exit()
        self.serverTabPage.exit()
        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        self.currentTabPage.unload()
        del self.title
        ShtikerPage.ShtikerPage.unload(self)

    def connectToMiniserver(self, doneEvent, username, ip, value=0):
        serverList = []
        serverPort = 7198
        gameServer = str(ip)
        for name in gameServer.split(';'):
            url = URLSpec(name, 1)
            if config.GetBool('server-force-ssl', False):
                url.setScheme('s')
            if not url.hasPort():
                url.setPort(serverPort)
            serverList.append(url)

        if len(serverList) == 1:
            failover = config.GetString('server-failover', '')
            serverURL = serverList[0]
            for arg in failover.split():
                try:
                    port = int(arg)
                    url = URLSpec(serverURL)
                    url.setPort(port)
                except:
                    url = URLSpec(arg, 1)
                else:
                    if url != serverURL:
                        serverList.append(url)

        if value == DGG.DIALOG_OK:
            base.cr._userLoggingOut = True
            if username:
                if username != '':
                    base.cr.playToken = username
            messenger.send(doneEvent, [serverList])

    def setMode(self, mode, updateAnyways=0):
        messenger.send('wakeup')
        if not updateAnyways:
            if self.mode == mode:
                return
            self.mode = mode
        if mode == PageMode.Current:
            self.mode = PageMode.Current
            self.title['text'] = TTLocalizer.ShardPageTitle
            self.currentTab['state'] = DGG.DISABLED
            self.currentTabPage.enter()
            self.serverTab['state'] = DGG.NORMAL
            self.serverTabPage.exit()
        else:
            if mode == PageMode.List:
                self.mode = PageMode.List
                self.title['text'] = TTLocalizer.ServerPageTitle
                self.currentTab['state'] = DGG.NORMAL
                self.currentTabPage.exit()
                self.serverTab['state'] = DGG.DISABLED
                self.serverTabPage.enter()
            else:
                raise StandardError, 'ServerPage::setMode - Invalid Mode %s' % mode


class ServerTabPage(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('ServerTabPage')

    def __init__(self, parent=aspect2d, _parent=None):
        self._parent = parent
        self.main = _parent
        DirectFrame.__init__(self, parent=self._parent, relief=None, pos=(0.0, 0.0,
                                                                          0.0), scale=(1.0,
                                                                                       1.0,
                                                                                       1.0))
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox').setTexture(loader.loadTexture('phase_3.5/maps/stickerbook_palette_4alla_6_blue.png', 'phase_3.5/maps/stickerbook_palette_4alla_6_a.rgb'), 1)
        self.unText = DirectLabel(parent=self, relief=None, text='Username', text_scale=0.05, text_align=TextNode.ACenter, pos=(0.575,
                                                                                                                                0,
                                                                                                                                0.625))
        self.unBox = DirectFrame(parent=self, relief=None, image=cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox'), pos=(0.575,
                                                                                                                 0,
                                                                                                                 0.525), scale=0.6)
        self.unInput = DirectEntry(parent=self.unBox, relief=DGG.GROOVE, scale=0.08, pos=(-0.33,
                                                                                          0,
                                                                                          -0.006), borderWidth=(0.05,
                                                                                                                0.05), frameColor=(
         (1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)), state=DGG.DISABLED, text_align=TextNode.ALeft, text_scale=TTLocalizer.OPCodesInputTextScale, width=10.5, numLines=1, focus=0, backgroundFocus=0, cursorKeys=1, text_fg=(0,
                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                    0,
                                                                                                                                                                                                                                    1), suppressMouse=1, autoCapitalize=0)
        self.moreInfo = None
        self.scrollList = None
        self.old = []
        self.indexToButton = {}
        self.load()
        return

    def load(self):
        self.serverTitle = ''
        self.miniservers = {}
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.helpText = DirectLabel(parent=self, relief=None, text='', text_scale=0.06, text_wordwrap=12, text_align=TextNode.ALeft, textMayChange=1, pos=(0.058,
                                                                                                                                                           0,
                                                                                                                                                           0.403))
        self.generateMiniserverList()
        self.generateScrollList()
        return

    def enter(self):
        taskMgr.doMethodLater(15, self.updateMiniserverList, 'updateList')
        self.show()

    def connectDialog(self, ip, name):
        self.ip = ip
        self.askDialog = TTDialog.TTGlobalDialog(doneEvent='doneAsking', dialogName='ConfirmConnectDialog', style=TTDialog.TwoChoice, text=TTLocalizer.ServerPageConnectDialog % name, text_wordwrap=15, command=self.connectToMiniserver)
        self.askDialog.show()
        self.askDialog.setBin('gui-popup', 1)
        self._parent.doneStatus = {'mode': 'exit', 'exitTo': 'closeShard'}
        self.accept('doneAsking', self.connectToMiniserver)

    def connectToMiniserver(self, val):
        self.askDialog.cleanup()
        del self.askDialog
        username = self.unInput.get()
        self.main.connectToMiniserver(self._parent.doneEvent, username, self.ip, value=val)

    def getServersFromAPI(self, id=''):
        if id:
            id = 'get/%s' % id
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'}
        request = urllib2.Request('https://ttoffline.com/api/miniservers/%s' % id, headers=headers)
        response = urllib2.urlopen(request)
        jdata = json.loads(response.read().decode())
        if id != '':
            if not jdata['success']:
                return (False, None)
        jdata2Dict = OrderedDict()
        vals = []
        for x in jdata:
            vals.append(jdata[x] if type(x) != dict else x)

        for y in range(0, len(jdata)):
            jdata2Dict[vals[y]['id'] if type(vals[y]) not in [bool, int] else y] = vals[y]

        return (
         True, jdata2Dict)

    def createMiniserverButton(self, servers, currentWordIndex, condition=False, updating=False):
        gui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        miniServerButton = DirectButton(parent=self, relief=None, text=servers[currentWordIndex]['name'], text_align=TextNode.ALeft, text_scale=0.05, text1_bg=self.textDownColor, text2_bg=self.textRolloverColor, text3_fg=self.textDisabledColor, textMayChange=0, command=self.showServerInfo, extraArgs=[
         currentWordIndex])
        nameLabel = DirectLabel(parent=hidden, relief=None, text=TTLocalizer.ServerPageName % servers[currentWordIndex]['name'], text_align=TextNode.ALeft, text_scale=0.06, text_wordwrap=12, pos=(0.058,
                                                                                                                                                                                                    0,
                                                                                                                                                                                                    0.375))
        gmLabel = DirectLabel(parent=hidden, relief=None, text=TTLocalizer.ServerPageGameMode % servers[currentWordIndex]['mode'], text_align=TextNode.ALeft, text_scale=0.06, text_wordwrap=12, pos=(0.058,
                                                                                                                                                                                                      0,
                                                                                                                                                                                                      0.25))
        descriptionLabel = DirectLabel(parent=hidden, relief=None, text=TTLocalizer.ServerPageDesc % servers[currentWordIndex]['desc'], text_align=TextNode.ALeft, text_scale=0.06, text_wordwrap=12, pos=(0.058,
                                                                                                                                                                                                           0,
                                                                                                                                                                                                           0.125))
        moreInfoLabel = DirectLabel(parent=hidden, relief=None, text=TTLocalizer.ServerPageMoreInfo, text_align=TextNode.ALeft, text_scale=0.06, text_wordwrap=12, pos=(0.058,
                                                                                                                                                                        0,
                                                                                                                                                                        -0.375))
        moreInfoButton = DirectButton(parent=hidden, image=(
         gui.find('**/QuitBtn_UP'), gui.find('**/QuitBtn_DN'),
         gui.find('**/QuitBtn_RLVR')), image_scale=(0.7, 1, 1), relief=None, text=TTLocalizer.ServerPageMoreInfoBtn, text_scale=0.05, text_pos=(0,
                                                                                                                                                -0.02), scale=1, pos=(0.7,
                                                                                                                                                                      0,
                                                                                                                                                                      -0.375), command=self.askMoreInfo, extraArgs=[
         servers[currentWordIndex]['id']])
        connectButton = DirectButton(parent=hidden, image=(
         gui.find('**/QuitBtn_UP'), gui.find('**/QuitBtn_DN'),
         gui.find('**/QuitBtn_RLVR'), gui.find('**/QuitBtn_UP')), image_scale=1.15, relief=None, text=TTLocalizer.ServerPageConnectBtn, text_scale=0.05, text_pos=(0,
                                                                                                                                                                   -0.02), scale=1, pos=(0.45,
                                                                                                                                                                                         0,
                                                                                                                                                                                         -0.6), command=self.connectDialog, extraArgs=[
         servers[currentWordIndex]['ip'], servers[currentWordIndex]['name']])
        connectInfo = DirectLabel(parent=hidden, relief=None, text='', text_align=TextNode.ACenter, text_scale=0.06, pos=(0.45,
                                                                                                                          0,
                                                                                                                          -0.4875))
        if not config.GetBool('want-mini-server', False):
            connectButton['state'] = DGG.DISABLED
            connectInfo['text'] = "Mini-Server mode isn't enabled!"
        else:
            if condition:
                connectButton['state'] = DGG.DISABLED
                connectInfo['text'] = 'Already on this server!'
        self.miniservers[miniServerButton] = [nameLabel, descriptionLabel, gmLabel,
         moreInfoLabel, moreInfoButton, connectButton,
         connectInfo, condition, currentWordIndex]
        self.indexToButton[currentWordIndex] = miniServerButton
        if servers[currentWordIndex]['ip'] not in self.old:
            self.old.append(servers[currentWordIndex]['ip'])
        if updating:
            self.scrollList.addItem(miniServerButton, True)
        gui.removeNode()
        return

    def removeMiniserverButton(self):
        buttonsToRemove = []
        for x in self.miniservers:
            isOnline, data = self.getServersFromAPI(id=self.miniservers[x][7])
            if not isOnline:
                buttonsToRemove.append(x)
                self.old.remove(self.miniservers[x][5]['extraArgs'][0])
                self.scrollList.removeItem(x, True)

        for button in buttonsToRemove:
            for obj in self.miniservers[button]:
                if type(obj) not in [bool, int]:
                    obj.hide()
                    obj.destroy()

            del self.miniservers[button]

    def generateMiniserverList(self, update=False):
        try:
            _, servers = self.getServersFromAPI()
            if len(servers) == 0:
                self.helpText['text'] = TTLocalizer.ServerPageNoMiniservers
            else:
                self.helpText['text'] = ''
            if update:
                if len(servers) > len(self.miniservers):
                    for x in servers:
                        if servers[x]['ip'] not in self.old:
                            self.createMiniserverButton(servers, servers[x]['id'], updating=update)

                else:
                    if len(servers) < len(self.miniservers):
                        self.removeMiniserverButton()
                return
            for x in servers:
                index = [ key for key, value in servers.iteritems() if value == servers[x] ][0]
                condition = True if servers[index]['ip'] == str(base.cr.serverList[0])[2:-5] else False
                if condition:
                    self.serverTitle = servers[index]['name']
                self.createMiniserverButton(servers, index, condition=condition)

        except Exception as e:
            self.notify.info('Could not connect to the miniserver API. (%s)' % e)
            self.helpText['text'] = TTLocalizer.ServerPageListOffline

        return

    def generateScrollList(self, updating=False):
        if not self.scrollList:
            gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
            self.scrollList = DirectScrolledList(parent=self, forceHeight=0.07, pos=(-0.5,
                                                                                     0,
                                                                                     0), incButton_image=(
             gui.find('**/FndsLst_ScrollUp'),
             gui.find('**/FndsLst_ScrollDN'),
             gui.find('**/FndsLst_ScrollUp_Rllvr'),
             gui.find('**/FndsLst_ScrollUp')), incButton_relief=None, incButton_scale=(1.3,
                                                                                       1.3,
                                                                                       -1.3), incButton_pos=(0.08,
                                                                                                             0,
                                                                                                             -0.6), incButton_image3_color=Vec4(1, 1, 1, 0.2), decButton_image=(
             gui.find('**/FndsLst_ScrollUp'),
             gui.find('**/FndsLst_ScrollDN'),
             gui.find('**/FndsLst_ScrollUp_Rllvr'),
             gui.find('**/FndsLst_ScrollUp')), decButton_relief=None, decButton_scale=(1.3,
                                                                                       1.3,
                                                                                       1.3), decButton_pos=(0.08,
                                                                                                            0,
                                                                                                            0.52), decButton_image3_color=Vec4(1, 1, 1, 0.2), itemFrame_pos=(-0.237,
                                                                                                                                                                             0,
                                                                                                                                                                             0.41), itemFrame_scale=1.0, itemFrame_relief=DGG.SUNKEN, itemFrame_frameSize=(-0.05,
                                                                                                                                                                                                                                                           0.66,
                                                                                                                                                                                                                                                           -0.98,
                                                                                                                                                                                                                                                           0.07), itemFrame_frameColor=(0.85,
                                                                                                                                                                                                                                                                                        0.95,
                                                                                                                                                                                                                                                                                        1,
                                                                                                                                                                                                                                                                                        1), itemFrame_borderWidth=(0.01,
                                                                                                                                                                                                                                                                                                                   0.01), numItemsVisible=14, items=self.miniservers.keys())
            gui.removeNode()
            return
        self.notify.info('Scroll list is already defined!')
        return

    def showServerInfo(self, serverNum):
        self.unText.show()
        self.unBox.show()
        self.unInput.show()
        for server in self.miniservers.keys():
            if self.miniservers[server][6] == True:
                server['state'] = DGG.DISABLED
            else:
                if server['state'] != DGG.NORMAL:
                    server['state'] = DGG.NORMAL
            if self.miniservers[server][5]['state'] == DGG.DISABLED:
                self.unInput.focusOutCommandFunc()
                self.unInput['state'] = DGG.DISABLED
                localAvatar.chatMgr.fsm.request('mainMenu')
            else:
                self.unInput['state'] = DGG.NORMAL
                localAvatar.chatMgr.fsm.request('otherDialog')
                self.unInput.focusInCommandFunc()

        for values in self.miniservers.values():
            for v in values:
                if type(v) not in [bool, int]:
                    if v.getParent() != hidden:
                        v.reparentTo(hidden)

        button = self.indexToButton[serverNum]
        for x in self.miniservers.keys():
            if x == button:
                x['state'] = DGG.DISABLED

        for obj in self.miniservers[button]:
            if type(obj) not in [bool, int]:
                obj.reparentTo(self)

    def askMoreInfo(self, id):
        self.serverId = id
        self.askDialog = TTDialog.TTGlobalDialog(doneEvent='doneAsking', dialogName='ConfirmInfoDialog', style=TTDialog.TwoChoice, text=TTLocalizer.ServerPageMoreInfoDialog, text_wordwrap=15, command=self.openMoreInformation)
        self.askDialog.show()
        self.askDialog.setBin('gui-popup', 1)
        self.accept('doneAsking', self.openMoreInformation)

    def openMoreInformation(self, value):
        self.askDialog.cleanup()
        del self.askDialog
        if value == DGG.DIALOG_OK:
            webbrowser.open('https://ttoffline.com/servers/' + str(self.serverId))

    def updateMiniserverList(self, task=None):
        self.generateMiniserverList(update=True)
        return Task.again

    def unload(self):
        self.miniservers = None
        self.scrollList.destroy()
        taskMgr.remove('updateList')
        del self.title
        del self.miniservers
        del self.scrollList
        self.unBox.destroy()
        self.unBox = None
        self.unInput.destroy()
        self.unInput = None
        return

    def destroy(self):
        self._parent = None
        DirectFrame.destroy(self)
        return

    def exit(self):
        taskMgr.remove('updateList')
        self.hide()

    def scrollListTo(self):
        self.scrollList.scrollTo(int(self.slider['value']))


class CurrentTabPage(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('CurrentTabPage')

    def __init__(self, parent=aspect2d, _parent=None):
        self._parent = parent
        self.main = _parent
        DirectFrame.__init__(self, parent=self._parent, relief=None, pos=(0.0, 0.0,
                                                                          0.0), scale=(1.0,
                                                                                       1.0,
                                                                                       1.0))
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.ShardInfoUpdateInterval = 5.0
        self.lowPop, self.midPop, self.highPop = base.getShardPopLimits()
        self.showPop = config.GetBool('show-total-population', 0)
        self.button = None
        self.ipBox = None
        self.load()
        return

    def destroy(self):
        self._parent = None
        DirectFrame.destroy(self)
        return

    def load(self):
        self.totalPopulationText = DirectLabel(parent=self, relief=None, text=TTLocalizer.ServerPagePopulation % 1, text_scale=0.08, text_wordwrap=24, textMayChange=1, text_align=TextNode.ACenter, pos=(0,
                                                                                                                                                                                                          0,
                                                                                                                                                                                                          0.4))
        self.totalPopulationText.show()
        self.titleText = DirectLabel(parent=self, relief=None, text=TTLocalizer.ServerPageName % base.cr.serverName, text_scale=0.08, text_wordwrap=24, textMayChange=1, text_align=TextNode.ACenter, pos=(0,
                                                                                                                                                                                                           0,
                                                                                                                                                                                                           0.5))
        self.titleText.show()
        self.descText = DirectLabel(parent=self, relief=None, text=TTLocalizer.InfoDescription + base.cr.serverDescription, text_scale=0.07, text_wordwrap=24, textMayChange=1, text_align=TextNode.ACenter, pos=(0,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0.3))
        self.descText.show()
        self.gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        self.listXorigin = -0.02
        self.listFrameSizeX = 0.67
        self.listZorigin = -0.96
        self.listFrameSizeZ = 1.04
        self.arrowButtonScale = 1.3
        self.itemFrameXorigin = -0.237
        self.itemFrameZorigin = 0.365
        self.ShardInfoUpdateInterval = 5.0
        self.buttonXstart = self.itemFrameXorigin + 0.293
        cdrGui = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        cdrGuiO = loader.loadModel('phase_3.5/models/gui/tt_m_gui_sbk_codeRedemptionGui')
        cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox').setTexture(loader.loadTexture('phase_3.5/maps/stickerbook_palette_4alla_6_blue.png', 'phase_3.5/maps/stickerbook_palette_4alla_6_a.rgb'), 1)
        cdrGuiO.find('**/tt_t_gui_sbk_cdrCodeBox').setTexture(loader.loadTexture('phase_3.5/maps/stickerbook_palette_4alla_6_purp.png', 'phase_3.5/maps/stickerbook_palette_4alla_6_a.rgb'), 1)
        self.changeServText = DirectLabel(parent=self, relief=None, text=TTLocalizer.ServerPageChangeServer, text_scale=0.12, text_align=TextNode.ACenter, pos=(0,
                                                                                                                                                                0,
                                                                                                                                                                -0.1))
        self.changeServText.show()
        conMethod = 'Connection Method: Mini-Server'
        if config.GetBool('want-mini-server', False):
            unX = -0.433
        else:
            unX = 0
            conMethod = 'Connection Method: Offline'
        self.changeServText = DirectLabel(parent=self, relief=None, text=conMethod, text_scale=0.07, text_align=TextNode.ACenter, pos=(0,
                                                                                                                                       0,
                                                                                                                                       -0.2))
        self.changeServText.show()
        self.unText = DirectLabel(parent=self, relief=None, text='Username', text_scale=0.07, text_align=TextNode.ACenter, pos=(unX, 0, -0.3))
        self.unBox = DirectFrame(parent=self, relief=None, image=cdrGui.find('**/tt_t_gui_sbk_cdrCodeBox'), pos=(unX, 0, -0.425), scale=0.8)
        self.unInput = DirectEntry(parent=self.unBox, relief=DGG.GROOVE, scale=0.08, pos=(-0.33,
                                                                                          0,
                                                                                          -0.006), borderWidth=(0.05,
                                                                                                                0.05), frameColor=(
         (1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)), state=DGG.NORMAL, text_align=TextNode.ALeft, text_scale=TTLocalizer.OPCodesInputTextScale, width=10.5, numLines=1, focus=1, backgroundFocus=0, cursorKeys=1, text_fg=(0,
                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                                  1), suppressMouse=1, autoCapitalize=0)
        if config.GetBool('want-mini-server', False):
            self.ipText = DirectLabel(parent=self, relief=None, text='Game Server', text_scale=0.07, text_align=TextNode.ACenter, pos=(0.433,
                                                                                                                                       0,
                                                                                                                                       -0.3))
            self.ipBox = DirectFrame(parent=self, relief=None, image=cdrGuiO.find('**/tt_t_gui_sbk_cdrCodeBox'), pos=(0.433,
                                                                                                                      0,
                                                                                                                      -0.425), scale=0.8)
            self.ipInput = DirectEntry(parent=self.ipBox, relief=DGG.GROOVE, scale=0.08, pos=(-0.33,
                                                                                              0,
                                                                                              -0.006), borderWidth=(0.05,
                                                                                                                    0.05), frameColor=(
             (1, 1, 1, 1), (1, 1, 1, 1), (0.5, 0.5, 0.5, 0.5)), state=DGG.NORMAL, text_align=TextNode.ALeft, text_scale=TTLocalizer.OPCodesInputTextScale, width=10.5, numLines=1, focus=0, backgroundFocus=0, cursorKeys=1, text_fg=(0,
                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                      1), suppressMouse=1, autoCapitalize=0)
        connectButtonGui = loader.loadModel('phase_3/models/gui/quit_button')
        self.connectButton = DirectButton(parent=self, relief=None, image=(connectButtonGui.find('**/QuitBtn_UP'),
         connectButtonGui.find('**/QuitBtn_DN'),
         connectButtonGui.find('**/QuitBtn_RLVR'),
         connectButtonGui.find('**/QuitBtn_UP')), image3_color=Vec4(0.5, 0.5, 0.5, 0.5), image_scale=1.15, state=DGG.NORMAL, text='Play', text_scale=TTLocalizer.OPCodesSubmitTextScale, text_align=TextNode.ACenter, text_pos=TTLocalizer.OPCodesSubmitTextPos, text3_fg=(0.5,
                                                                                                                                                                                                                                                                           0.5,
                                                                                                                                                                                                                                                                           0.5,
                                                                                                                                                                                                                                                                           0.75), textMayChange=0, pos=(0,
                                                                                                                                                                                                                                                                                                        0.0,
                                                                                                                                                                                                                                                                                                        -0.6104), command=self.connectDialog)
        cdrGui.removeNode()
        connectButtonGui.removeNode()
        return

    def enter(self):
        self.show()
        self.unInput.enterText('')
        if self.ipBox:
            self.ipInput.enterText('')
        self.askForShardInfoUpdate()
        localAvatar.chatMgr.fsm.request('otherDialog')
        self.accept('shardInfoUpdated', self.updatePopulation)

    def updatePopulation(self):
        curShardTuples = base.cr.listActiveShards()

        def compareShardTuples(a, b):
            if a[1] < b[1]:
                return -1
            if b[1] < a[1]:
                return 1
            return 0

        curShardTuples.sort(compareShardTuples)
        totalPop = 0
        for i in range(len(curShardTuples)):
            shardId, name, pop, WVPop = curShardTuples[i]
            totalPop += pop

        if totalPop == 0:
            totalPop = 16
        self.totalPopulationText['text'] = TTLocalizer.ServerPagePopulation % totalPop
        if self.button:
            self.button.destroy()
        self.button = self.makeShardButton(totalPop)

    def askForShardInfoUpdate(self, task=None):
        ToontownDistrictStats.refresh('shardInfoUpdated')
        taskMgr.doMethodLater(self.ShardInfoUpdateInterval, self.askForShardInfoUpdate, 'ShardPageUpdateTask-doLater')
        return Task.done

    def makeShardButton(self, shardPop):
        model = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = model.find('**/minnieCircle')
        shardButtonR = DirectButton(parent=self, relief=None, image=button, image_scale=(0.5,
                                                                                         1,
                                                                                         0.5), image2_scale=(0.583,
                                                                                                             1,
                                                                                                             0.583), image_color=self.getPopColor(shardPop), pos=(-0.4,
                                                                                                                                                                  0,
                                                                                                                                                                  0.42), text=self.getPopText(shardPop), text_scale=0.06, text_align=TextNode.ACenter, text_pos=(-0.0125,
                                                                                                                                                                                                                                                                 -0.0125), text_fg=Vec4(0, 0, 0, 0), text1_fg=Vec4(0, 0, 0, 0), text2_fg=Vec4(0, 0, 0, 1), text3_fg=Vec4(0, 0, 0, 0))
        del model
        del button
        return shardButtonR

    def getPopColor(self, pop):
        if config.GetBool('want-lerping-pop-colors', False):
            if pop < self.midPop:
                color1 = POP_COLORS_NTT[0]
                color2 = POP_COLORS_NTT[1]
                popRange = self.midPop - self.lowPop
                pop = pop - self.lowPop
            else:
                color1 = POP_COLORS_NTT[1]
                color2 = POP_COLORS_NTT[2]
                popRange = self.highPop - self.midPop
                pop = pop - self.midPop
            popPercent = pop / float(popRange)
            if popPercent > 1:
                popPercent = 1
            newColor = color2 * popPercent + color1 * (1 - popPercent)
        else:
            if pop < self.lowPop:
                newColor = POP_COLORS[0]
            else:
                if pop < self.midPop:
                    newColor = POP_COLORS[1]
                else:
                    newColor = POP_COLORS[2]
        return newColor

    def getPopText(self, pop):
        if pop < self.lowPop:
            popText = TTLocalizer.ShardPageLow
        else:
            if pop < self.midPop:
                popText = TTLocalizer.ShardPageMed
            else:
                popText = TTLocalizer.ShardPageHigh
        return popText

    def exit(self):
        self.hide()
        self.ignore('shardInfoUpdated')
        self.ignore('currentTitle')
        self.ignore('confirmDone')
        localAvatar.chatMgr.fsm.request('mainMenu')
        taskMgr.remove('ShardPageUpdateTask-doLater')

    def unload(self):
        if self.ipBox:
            self.ipBox.destroy()
            self.ipBox = None
            self.ipInput.destroy()
            self.ipInput = None
        self.unBox.destroy()
        self.unBox = None
        self.unInput.destroy()
        self.unInput = None
        self.connectButton.destroy()
        self.connectButton = None
        self.gui.removeNode()
        taskMgr.remove('ShardPageUpdateTask-doLater')
        return

    def connectDialog(self):
        self.askDialog = TTDialog.TTGlobalDialog(doneEvent='doneAsking', dialogName='ConfirmConnectDialog', style=TTDialog.TwoChoice, text=TTLocalizer.ServerPageConnectDialogExt, text_wordwrap=15, command=self.connect)
        self.askDialog.show()
        self.askDialog.setBin('gui-popup', 1)
        self._parent.doneStatus = {'mode': 'exit', 'exitTo': 'closeShard'}
        self.accept('doneAsking', self.connect)

    def connect(self, val=None):
        self.askDialog.cleanup()
        del self.askDialog
        input = base.cr.launcher.getGameServer()
        if input == None:
            input = '127.0.0.1'
        if self.ipBox:
            if self.ipInput.get() != '':
                input = self.ipInput.get()
        username = self.unInput.get()
        self._parent.doneStatus = {'mode': 'exit', 'exitTo': 'closeShard'}
        self.main.connectToMiniserver(self._parent.doneEvent, username, input, value=val)
        return