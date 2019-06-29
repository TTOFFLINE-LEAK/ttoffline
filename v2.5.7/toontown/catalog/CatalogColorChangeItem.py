import CatalogItem
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from otp.otpgui.OTPDialog import YesNo, Acknowledge
import time

class CatalogColorChangeItem(CatalogItem.CatalogItem):

    def makeNewItem(self, colorIndex):
        self.colorIndex = colorIndex
        CatalogItem.CatalogItem.makeNewItem(self)

    def getDeliveryTime(self):
        return 1

    def getBasePrice(self):
        return 300

    def getPurchaseLimit(self):
        return 1

    def getTypeName(self):
        return TTLocalizer.ColorTypeName

    def getName(self):
        return TTLocalizer.NumToColor[self.colorIndex]

    def getPicture(self, avatar):
        frame = self.makeFrame()
        model = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        sample = model.find('**/big_book')
        sample.setScale(2)
        sample.setTransparency(True)
        sample.setTexture(self.loadTexture(), 1)
        sample.setColorScale(base.localAvatar.style.getColorFromIndex(self.colorIndex))
        sample.reparentTo(frame)
        self.hasPicture = True
        return (
         frame, None)

    def loadTexture(self):
        from panda3d.core import Texture
        texture = loader.loadTexture('phase_6/maps/Kartmenu_paintbucket.jpg', 'phase_6/maps/Kartmenu_paintbucket_a.rgb')
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        return texture

    def reachedPurchaseLimit(self, avatar):
        if self in avatar.onOrder or self in avatar.mailboxContents or self in avatar.onGiftOrder or self in avatar.awardMailboxContents or self in avatar.onAwardOrder:
            return 1
        return 0

    def isGift(self):
        return False

    def acceptItem(self, mailbox, index, callback):
        self.mailbox = mailbox
        self.index = index
        self.callback = callback
        if base.localAvatar.style.headColor in (0, 26):
            message = TTLocalizer.MessageConfirmColorSpecial % TTLocalizer.NumToColor[self.colorIndex]
        else:
            message = TTLocalizer.MessageConfirmColor % TTLocalizer.NumToColor[self.colorIndex]
        dialogClass = ToontownGlobals.getDialogClass()
        self.dialog = dialogClass(text=message, dialogName='acceptItem', command=self.__handleAccepted, style=YesNo)
        self.dialog.show()

    def __handleAccepted(self, status):
        self.dialog.cleanup()
        if status == 1:
            msg = TTLocalizer.MessageColorConfirmed % TTLocalizer.NumToColor[self.colorIndex]
            dialogClass = ToontownGlobals.getDialogClass()
            self.dialog = dialogClass(text=msg, dialogName='postAccept', command=self.__finished, style=Acknowledge)
            self.dialog.show()
        else:
            self.callback(ToontownGlobals.P_UserCancelled, None, self.index)
        return

    def __finished(self, status):
        self.dialog.cleanup()
        del self.dialog
        self.mailbox.acceptItem(self, self.index, self.callback)
        del self.mailbox
        del self.callback

    def getHashContents(self):
        return self.colorIndex

    def decodeDatagram(self, di, versionNumber, store):
        CatalogItem.CatalogItem.decodeDatagram(self, di, versionNumber, store)
        self.colorIndex = di.getUint16()

    def encodeDatagram(self, dg, store):
        CatalogItem.CatalogItem.encodeDatagram(self, dg, store)
        dg.addUint16(self.colorIndex)

    def recordPurchase(self, avatar, optional):
        avatar.d_setNewColor(self.colorIndex)
        return ToontownGlobals.P_ItemAvailable