from direct.directnotify import DirectNotifyGlobal
from toontown.estate.DistributedFurnitureItemAI import DistributedFurnitureItemAI
from toontown.toonbase import ToontownGlobals
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogInvalidItem import CatalogInvalidItem
from toontown.catalog.CatalogItemList import CatalogItemList
from DistributedNPCToonBaseAI import *
from direct.task.Task import Task
import time

class DistributedNPCPrizeClerkAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.timedOut = 0
        self.givesQuests = 0
        self.movie = None
        self.customerId = None
        return

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        self.customerId = None
        DistributedNPCToonBaseAI.delete(self)
        return

    def __verifyAvatarInMyZone(self, av):
        return av.getLocation() == self.getLocation()

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.air.doId2do.has_key(avId):
            self.notify.warning('Avatar: %s not found' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return
        av = self.air.doId2do[avId]
        if not self.__verifyAvatarInMyZone(av):
            self.air.writeServerEvent('suspicious', avId=av.getDoId(), issue='Tried to avatarEnter without being in same location.')
            return
        self.customerId = avId
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])
        flag = NPCToons.PURCHASE_MOVIE_START
        av = self.air.doId2do.get(avId)
        house = self.air.doId2do.get(av.houseId)
        if house:
            numItems = len(house.interiorItems) + len(house.atticItems) + len(house.atticWallpaper) + len(house.atticWindows) + len(house.interiorWallpaper) + len(house.interiorWindows)
            self.sendUpdateToAvatarId(avId, 'setLimits', [numItems])
        else:
            self.air.dbInterface.queryObject(self.air.dbId, av.houseId, self.__gotHouse)
        self.sendShoppingMovie(avId, flag)
        DistributedNPCToonBaseAI.avatarEnter(self)

    def __gotHouse(self, dclass, fields):
        if dclass != self.air.dclassesByName['DistributedHouseAI']:
            return
        numItems = len(CatalogItemList(fields['setInteriorItems'][0], store=CatalogItem.Customization)) + len(CatalogItemList(fields['setAtticItems'][0], store=CatalogItem.Customization)) + len(CatalogItemList(fields['setAtticWallpaper'][0], store=CatalogItem.Customization)) + len(CatalogItemList(fields['setAtticWindows'][0], store=CatalogItem.Customization)) + len(CatalogItemList(fields['setInteriorWallpaper'][0], store=CatalogItem.Customization)) + len(CatalogItemList(fields['setInteriorWindows'][0], store=CatalogItem.Customization))
        self.sendUpdateToAvatarId(fields['setAvatarId'][0], 'setLimits', [numItems])

    def sendShoppingMovie(self, avId, flag):
        self.busy = avId
        self.sendUpdate('setMovie', [flag,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(NPCToons.TAILOR_COUNTDOWN_TIME, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a Toonfest Prize Person!')

    def sendTimeoutMovie(self, task):
        toon = self.air.doId2do.get(self.customerId)
        self.timedOut = 1
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        self.customerId = None
        self.busy = 0
        self.timedOut = 0
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_CLEAR,
         self.npcId,
         0,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        return Task.done

    def completePurchase(self, avId):
        self.busy = avId
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_COMPLETE,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        return

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        if self.customerId == avId:
            toon = self.air.doId2do.get(avId)
            if toon == None:
                toon = DistributedToonAI.DistributedToonAI(self.air)
                toon.doId = avId
        else:
            self.notify.warning('invalid customer avId: %s, customerId: %s ' % (avId, self.customerId))
        if self.busy == avId:
            self.sendClearMovie(None)
        else:
            self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        return

    def setMovie(self, todo0, todo1, todo2, todo3):
        pass

    def requestPrize(self, context, item, optional):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId=avId, issue='Used phone from other shard!')
            return
        item = CatalogItem.getItem(item)
        if isinstance(item, CatalogInvalidItem):
            self.air.writeServerEvent('suspicious', avId=avId, issue='Tried to purchase invalid catalog item.')
            return
        price = item.getPrice(0)
        if item.getDeliveryTime():
            if len(av.onOrder) > 3:
                self.sendUpdateToAvatarId(avId, 'd_requestPrizeInfo', [context, ToontownGlobals.P_OnOrderListFull])
                self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_DELIVERY_FULL,
                 self.npcId,
                 avId,
                 ClockDelta.globalClockDelta.getRealNetworkTime()])
                return
            if len(av.mailboxContents) + len(av.onOrder) >= ToontownGlobals.MaxMailboxContents:
                self.sendUpdateToAvatarId(avId, 'd_requestPrizeInfo', [context, ToontownGlobals.P_MailboxFull])
                self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_MAIL_FULL,
                 self.npcId,
                 avId,
                 ClockDelta.globalClockDelta.getRealNetworkTime()])
            if not av.takeTokens(price):
                return
            if av.instantDelivery:
                item.deliveryDate = int(time.time() / 60)
            else:
                item.deliveryDate = int(time.time() / 60) + item.getDeliveryTime()
            av.onOrder.append(item)
            av.b_setDeliverySchedule(av.onOrder)
            self.sendUpdateToAvatarId(avId, 'd_requestPrizeInfo', [context, ToontownGlobals.P_ItemOnOrder])
            self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_ITEM_BOUGHT,
             self.npcId,
             avId,
             ClockDelta.globalClockDelta.getRealNetworkTime()])
        else:
            if not av.takeTokens(price):
                return
            resp = item.recordPurchase(av, optional)
            if resp < 0:
                av.addTokens(price)
            self.sendUpdateToAvatarId(avId, 'd_requestPrizeInfo', [context, resp])

    def requestFinished(self):
        avId = self.air.getAvatarIdFromSender()
        self.completePurchase(avId)