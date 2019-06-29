from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from toontown.catalog import CatalogGenerator, CatalogItemPanel, CatalogInvalidItem, CatalogItemTypes
from toontown.toonbase import ToontownGlobals
from panda3d.core import Vec4, TextNode
NUM_CATALOG_ROWS = 3
NUM_CATALOG_COLS = 2

class ToonfestPrizeCollect(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonfestPrizeCollect')

    def __init__(self, parent=aspect2d, **kw):
        self.guiItems = loader.loadModel('phase_6/models/gui/ttr_m_tf_gui_PrizePanel')
        background = self.guiItems.find('**/prizePanelMain')
        optiondefs = (('scale', 1.0, None),
         (
          'pos', (-0.5, 1.0, 0.025), None),
         ('npc', None, None),
         ('random', None, None),
         ('doneEvent', None, None),
         (
          'image', background, None),
         ('relief', None, None))
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.generator = CatalogGenerator.CatalogGenerator()
        self.gifting = -1
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.load()
        self.initialiseoptions(ToonfestPrizeCollect)
        self.setMaxPageIndex(self.numNewPages)
        self.setPageIndex(0)
        self.showPageItems()
        self.hide()
        return

    def show(self):
        self.accept('CatalogItemPurchaseRequest', self.__handlePurchaseRequest)
        self.accept(base.localAvatar.uniqueName('tokenChange'), self.__tokenChange)
        self.accept('setDeliverySchedule-%s' % base.localAvatar.doId, self.remoteUpdate)
        DirectFrame.show(self)

    def hide(self):
        self.ignore('CatalogItemPurchaseRequest')
        self.ignore('CatalogItemGiftPurchaseRequest')
        self.ignore(base.localAvatar.uniqueName('tokenChange'))
        self.ignore('setDeliverySchedule-%s' % base.localAvatar.doId)
        DirectFrame.hide(self)

    def setNumPages(self, numNewPages):
        self.numNewPages = numNewPages

    def setPageIndex(self, index):
        self.pageIndex = index

    def setMaxPageIndex(self, numPages):
        self.maxPageIndex = max(numPages - 1, -1)

    def showItems(self, index=None):
        messenger.send('wakeup')
        self.setMaxPageIndex(self.numPages)
        if self.numPages == 0:
            self.setPageIndex(-1)
        else:
            if index is not None:
                self.setPageIndex(index)
            else:
                self.setPageIndex(0)
        self.showPageItems()
        return

    def showNextPage(self):
        messenger.send('wakeup')
        self.pageIndex = self.pageIndex + 1
        self.pageIndex = min(self.pageIndex, self.maxPageIndex)
        self.showPageItems()

    def showBackPage(self):
        messenger.send('wakeup')
        self.pageIndex = self.pageIndex - 1
        self.pageIndex = max(self.pageIndex, -1)
        self.showPageItems()

    def showPageItems(self):
        self.hidePages()
        page = self.pageList[self.pageIndex]
        page.show()
        for panel in self.panelDict[page.get_key()]:
            panel.load()
            if panel.ival:
                panel.ival.loop()
            self.visiblePanels.append(panel)

        if self.pageIndex < self.maxPageIndex:
            self.nextPageButton.show()
        else:
            self.nextPageButton.hide()
        if self.pageIndex > 0:
            self.backPageButton.show()
        else:
            self.backPageButton.hide()
        self.adjustForSound()
        self.update()

    def adjustForSound(self):
        numEmoteItems = 0
        emotePanels = []
        for visIndex in xrange(len(self.visiblePanels)):
            panel = self.visiblePanels[visIndex]
            item = panel['item']
            catalogType = item.getTypeCode()
            if catalogType == CatalogItemTypes.EMOTE_ITEM:
                numEmoteItems += 1
                emotePanels.append(panel)
            else:
                panel.soundOnButton.hide()
                panel.soundOffButton.hide()

        if numEmoteItems == 1:
            emotePanels[0].handleSoundOnButton()
        else:
            if numEmoteItems > 1:
                for panel in emotePanels:
                    panel.handleSoundOffButton()

    def hidePages(self):
        for page in self.pageList:
            page.hide()

        for panel in self.visiblePanels:
            if panel.ival:
                panel.ival.finish()

        self.visiblePanels = []

    def packPages(self, panelList, pageList, prefix):
        i = 0
        j = 0
        itemIndex = 0
        numPages = 0
        pageName = prefix + '_page%d' % numPages
        for item in panelList:
            if i == 0 and j == 0:
                itemIndex = 0
                numPages += 1
                pageName = prefix + '_page%d' % numPages
                page = self.base.attachNewNode(pageName)
                pageList.append(page)
            locator = self.guiItems.find('**/item_panel_%d' % itemIndex).copyTo(page)
            item.reparentTo(locator)
            itemList = self.panelDict.get(page.get_key(), [])
            itemList.append(item)
            self.panelDict[page.get_key()] = itemList
            itemIndex += 1
            j += 1
            if j == NUM_CATALOG_COLS:
                j = 0
                i += 1
            if i == NUM_CATALOG_ROWS:
                i = 0

        return numPages

    def load(self):
        self.pageIndex = -1
        self.maxPageIndex = 0
        self.numNewPages = 0
        self.panelList = []
        self.pageList = []
        self.panelDict = {}
        self.visiblePanels = []
        self.responseDialog = None
        self.base = DirectLabel(self, relief=None, image=self.guiItems.find('**/prizePanelMain'))
        oldLift = 0.4
        lift = 0.4
        liftDiff = lift - oldLift
        lift2 = 0.05
        smash = 0.75
        priceScale = 0.15
        self.squares = [[], [], [], []]
        for i in range(NUM_CATALOG_ROWS):
            for j in range(NUM_CATALOG_COLS):
                label = DirectLabel(self.base, relief=None, state='normal')
                self.squares[i].append(label)

        def priceSort(a, b, type):
            priceA = a.getPrice(type)
            priceB = b.getPrice(type)
            return priceB - priceA

        itemList = self.generator.generateTFPrizeCatalog(base.localAvatar)
        for item in itemList:
            if isinstance(item, CatalogInvalidItem.CatalogInvalidItem):
                self.notify.warning('skipping catalog invalid item %s' % item)
                continue
            else:
                self.panelList.append(CatalogItemPanel.CatalogItemPanel(parent=hidden, item=item, parentCatalogScreen=self, useTokens=True))

        numPages = self.packPages(self.panelList, self.pageList, 'new')
        self.setNumPages(numPages)
        exitButton = self.guiItems.find('**/cancelIcon')
        exitButtonRollover = self.guiItems.find('**/cancelIcon_rollover')
        exitButtonPressed = self.guiItems.find('**/cancelIcon_pressed')
        self.exitButton = DirectButton(self, relief=None, image=[exitButton,
         exitButtonPressed,
         exitButtonRollover,
         exitButtonPressed], command=self.exit)
        self.exitButton.setBin('gui-popup', 50)
        jarGui = loader.loadModel('phase_6/models/gui/ttr_m_tf_gui_tokens')
        jarOrigin = self.guiItems.find('**/jar_origin')
        jarOrigin.reparentTo(self)
        self.tokenJar = DirectLabel(jarOrigin, relief=None, image=jarGui.find('**/jar'), text=str(base.localAvatar.getTokens()), text_align=TextNode.ACenter, text_scale=0.2, text_pos=(0.0,
                                                                                                                                                                                        -0.1), text_fg=(0.95,
                                                                                                                                                                                                        0.95,
                                                                                                                                                                                                        0,
                                                                                                                                                                                                        1), text_shadow=(0,
                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                         0,
                                                                                                                                                                                                                         1), text_font=ToontownGlobals.getSignFont())
        nextUp = self.guiItems.find('**/arrowRight')
        nextRollover = self.guiItems.find('**/arrowRight_rollover')
        nextDown = self.guiItems.find('**/arrowRight_pressed')
        nextInactive = self.guiItems.find('**/arrowRight_inactive')
        prevUp = self.guiItems.find('**/arrowLeft')
        prevRollover = self.guiItems.find('**/arrowLeft_rollover')
        prevDown = self.guiItems.find('**/arrowLeft_pressed')
        prevInactive = self.guiItems.find('**/arrowLeft_inactive')
        self.nextPageButton = DirectButton(self, relief=None, image=[nextUp,
         nextDown,
         nextRollover,
         nextInactive], command=self.showNextPage)
        self.backPageButton = DirectButton(self, relief=None, image=[prevUp,
         prevDown,
         prevRollover,
         prevInactive], command=self.showBackPage)
        self.backPageButton.hide()
        return

    def reload(self):
        for panel in self.panelList:
            panel.destroy()

        def priceSort(a, b, type):
            priceA = a.getPrice(type)
            priceB = b.getPrice(type)
            return priceB - priceA

        self.pageIndex = -1
        self.maxPageIndex = 0
        self.numPages = 0
        self.panelList = []
        self.pageList = []
        self.panelDict = {}
        self.visiblePanels = []
        itemList = self.generator.generateTFPrizeCatalog(base.localAvatar.doId)
        itemList.reverse()
        for item in itemList:
            self.panelList.append(CatalogItemPanel.CatalogItemPanel(parent=hidden, item=item, useTokens=True))

        numPages = self.packPages(self.panelList, self.pageList, 'new')
        self.setNumPages(numPages)
        self.setMaxPageIndex(self.numNewPages)
        self.setPageIndex(-1)
        self.showPageItems()

    def unload(self):
        self.hide()
        self.exitButton.hide()
        self.destroy()
        del self.base
        del self.squares
        for panel in self.panelList:
            panel.destroy()

        del self.generator
        del self.panelList
        del self.exitButton
        del self.tokenJar
        del self.nextPageButton
        del self.backPageButton
        if self.responseDialog:
            self.responseDialog.cleanup()
            self.responseDialog = None
        return

    def exit(self):
        messenger.send(self['doneEvent'])
        self.unload()

    def remoteUpdate(self):
        self.update()

    def update(self, lock=0):
        avatarTokens = base.localAvatar.getTokens()
        if hasattr(self, 'tokenJar'):
            self.tokenJar['text'] = str(avatarTokens)
            if lock == 0:
                for item in self.panelList:
                    if type(item) != type(''):
                        item.updateButtons(0)

    def __handlePurchaseRequest(self, item):
        print item
        item.requestPurchase(self['npc'], self.__handlePurchaseResponse)

    def __handlePurchaseResponse(self, retCode, item):
        if retCode == ToontownGlobals.P_UserCancelled:
            self.update()
            return

    def __clearDialog(self, event):
        self.responseDialog.cleanup()
        self.responseDialog = None
        return

    def __tokenChange(self, money):
        self.update(0)