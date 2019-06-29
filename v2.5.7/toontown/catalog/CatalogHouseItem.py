from panda3d.core import NodePath, TransparencyAttrib
import CatalogItem, random
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from otp.otpbase import OTPLocalizer
from direct.interval.IntervalGlobal import *
from toontown.estate import HouseGlobals
from direct.actor import Actor

class CatalogHouseItem(CatalogItem.CatalogItem):
    sequenceNumber = 0

    def makeNewItem(self, itemIndex=0, tagCode=1):
        self.houseIndex = itemIndex
        self.giftCode = tagCode
        CatalogItem.CatalogItem.makeNewItem(self)

    def getPurchaseLimit(self):
        return 1

    def reachedPurchaseLimit(self, avatar):
        if self in avatar.onOrder or self in avatar.mailboxContents or self in avatar.onGiftOrder or self in avatar.awardMailboxContents or self in avatar.onAwardOrder:
            return 1
        return 0

    def getAcceptItemErrorText(self, retcode):
        if retcode == ToontownGlobals.P_ItemAvailable:
            return TTLocalizer.CatalogAcceptHouse
        return CatalogItem.CatalogItem.getAcceptItemErrorText(self, retcode)

    def saveHistory(self):
        return 1

    def getTypeName(self):
        return TTLocalizer.HouseTypeName

    def getName(self):
        name = TTLocalizer.HouseNames[self.houseIndex]
        return name

    def recordPurchase(self, avatar, optional):
        if avatar:
            avatar.setHouseType(self.houseIndex)
        return ToontownGlobals.P_ItemAvailable

    def setHouseColor(self, colorChoice):
        bwall = self.model.find('**/*back')
        rwall = self.model.find('**/*right')
        fwall = self.model.find('**/*front')
        lwall = self.model.find('**/*left')
        kd = 0.8
        color = HouseGlobals.houseColors[colorChoice]
        dark = (kd * color[0], kd * color[1], kd * color[2])
        if not bwall.isEmpty():
            bwall.setColor(color[0], color[1], color[2], 1)
        if not fwall.isEmpty():
            fwall.setColor(color[0], color[1], color[2], 1)
        if not rwall.isEmpty():
            rwall.setColor(dark[0], dark[1], dark[2], 1)
        if not lwall.isEmpty():
            lwall.setColor(dark[0], dark[1], dark[2], 1)
        aColor = HouseGlobals.atticWood
        attic = self.model.find('**/attic')
        if not attic.isEmpty():
            attic.setColor(aColor[0], aColor[1], aColor[2], 1)
        color = HouseGlobals.houseColors2[colorChoice]
        chimneyList = self.model.findAllMatches('**/chim*')
        for chimney in chimneyList:
            chimney.setColor(color[0], color[1], color[2], 1)

    def getPicture(self, avatar):
        photoModel = HouseGlobals.houseModels[self.houseIndex]
        self.model = loader.loadModel(photoModel)
        frame = self.makeFrame()
        self.model.reparentTo(frame)
        if self.houseIndex == 0:
            self.setHouseColor(random.randrange(0, 5))
        photoPos = (0, 0, -1.05)
        self.model.setPos(*photoPos)
        photoScale = 0.075 if self.houseIndex != HouseGlobals.HOUSE_CASTLE else 0.04
        self.model.setScale(photoScale)
        self.model.setBin('unsorted', 0, 1)
        self.model.setDepthTest(True)
        self.model.setDepthWrite(True)
        self.model.setTransparency(TransparencyAttrib.MDual, 1)
        self.rotIval = self.model.hprInterval(10, (0, 0, 0), (360, 0, 0))
        self.rotIval.loop()
        self.hasPicture = True
        return (
         frame, None)

    def cleanupPicture(self):
        CatalogItem.CatalogItem.cleanupPicture(self)
        self.rotIval.finish()
        self.model.detachNode()
        self.model = None
        return

    def output(self, store=-1):
        return 'CatalogHouseItem(%s%s)' % (self.houseIndex, self.formatOptionalData(store))

    def getHashContents(self):
        return self.houseIndex

    def getBasePrice(self):
        return 2000

    def decodeDatagram(self, di, versionNumber, store):
        CatalogItem.CatalogItem.decodeDatagram(self, di, versionNumber, store)
        self.houseIndex = di.getUint8()

    def encodeDatagram(self, dg, store):
        CatalogItem.CatalogItem.encodeDatagram(self, dg, store)
        dg.addUint8(self.houseIndex)

    def getRequestPurchaseErrorText(self, retcode):
        retval = CatalogItem.CatalogItem.getRequestPurchaseErrorText(self, retcode)
        if retval == TTLocalizer.CatalogPurchaseItemAvailable:
            retval = TTLocalizer.CatalogPurchaseHouseAvailable
        return retval

    def getRequestPurchaseErrorTextTimeout(self):
        return 20

    def getDeliveryTime(self):
        return 0

    def compareTo(self, other):
        return self.houseIndex - other.houseIndex

    def reachedPurchaseLimit(self, avatar):
        return 0

    def isGift(self):
        return 0