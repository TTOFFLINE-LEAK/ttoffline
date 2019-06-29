from panda3d.core import *
from panda3d.direct import *
from DistributedNPCToonBase import *
from toontown.minigame import ClerkPurchase
from direct.showbase.RandomNumGen import RandomNumGen
from toontown.shtiker.PurchaseManagerConstants import *
from direct.task.Task import Task
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
from toontown.toontowngui import TeaserPanel
from otp.nametag.NametagConstants import *
from toontown.toonfest import ToonfestPrizeCollect
from toontown.catalog import CatalogItem
import NPCToons
DONE_EVENT = 'prizeGuiDone'
MODE_TO_PHRASE = {NPCToons.PURCHASE_MOVIE_NO_MONEY: TTLocalizer.TF_STOREOWNER_NOMONEY, NPCToons.PURCHASE_MOVIE_ITEM_BOUGHT: TTLocalizer.TF_STOREOWNER_BOUGHT, 
   NPCToons.PURCHASE_MOVIE_ITEM_LIMIT: TTLocalizer.TF_STOREOWNER_LIMIT, 
   NPCToons.PURCHASE_MOVIE_ITEM_FULL: TTLocalizer.TF_STOREOWNER_FULL, 
   NPCToons.PURCHASE_MOVIE_ITEM_INVALID: TTLocalizer.TF_STOREOWNER_INVALID, 
   NPCToons.PURCHASE_MOVIE_MAIL_FULL: TTLocalizer.TF_STOREOWNER_MAILFULL, 
   NPCToons.PURCHASE_MOVIE_DELIVERY_FULL: TTLocalizer.TF_STOREOWNER_DELIVERYFULL}

class DistributedNPCPrizeClerk(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.rng = None
        self.gui = None
        self.isLocalToon = 0
        self.av = None
        self.numHouseItems = None
        return

    def announceGenerate(self):
        DistributedNPCToonBase.announceGenerate(self)
        self.rng = RandomNumGen(self.doId)
        self.setHat(59, 0, 0)
        if self.style.gender == 'm':
            self.setGlasses(22, 0, 0)

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPrizeGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.gui:
            self.gui.exit()
            self.gui = None
        self.av = None
        base.localAvatar.posCamera(0, 0)
        DistributedNPCToonBase.disable(self)
        return

    def allowedToEnter(self):
        if hasattr(base, 'ttAccess') and base.ttAccess and base.ttAccess.canAccess():
            return True
        return False

    def handleOkTeaser(self):
        self.dialog.destroy()
        del self.dialog
        place = base.cr.playGame.getPlace()
        if place:
            place.fsm.request('walk')

    def handleCollisionSphereEnter(self, collEntry):
        if self.allowedToEnter():
            base.cr.playGame.getPlace().fsm.request('purchase')
            self.sendUpdate('avatarEnter', [])
        else:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('stopped')
            self.dialog = TeaserPanel.TeaserPanel(pageName='otherGags', doneFunc=self.handleOkTeaser)

    def initToonState(self):
        self.setAnimState('neutral', 1.05, None, None)
        npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_prizeclerk_origin_%s;+s' % self.posIndex)
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.clearMat()
        else:
            self.notify.warning('announceGenerate: Could not find npc_prizeclerk_origin_' + str(self.posIndex))
        return

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        return

    def resetClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPrizeGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.gui:
            self.gui.exit()
            self.gui = None
        self.clearMat()
        self.startLookAround()
        self.detectAvatars()
        if self.isLocalToon:
            self.freeAvatar()
        return Task.done

    def setLimits(self, numHouseItems):
        self.numHouseItems = numHouseItems

    def setMovie(self, mode, npcId, avId, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = NPCToons.CLERK_COUNTDOWN_TIME - timeStamp
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.PURCHASE_MOVIE_CLEAR:
            return
        if mode == NPCToons.PURCHASE_MOVIE_START:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                camera.wrtReparentTo(render)
                self.cameraLerp = LerpPosQuatInterval(camera, 1, Point3(-4, 16, self.getHeight() - 0.5), Point3(-150, -2, 0), other=self, blendType='easeInOut')
                self.cameraLerp.start()
            self.setChatAbsolute(self.rng.choice(TTLocalizer.TF_STOREOWNER_GREETING), CFSpeech | CFTimeout)
            if self.isLocalToon:
                taskMgr.doMethodLater(1.0, self.popupPrizeGUI, self.uniqueName('popupPrizeGUI'))
        else:
            if MODE_TO_PHRASE.has_key(mode):
                self.setChatAbsolute(self.rng.choice(MODE_TO_PHRASE[mode]), CFSpeech | CFTimeout)
            else:
                if mode == NPCToons.PURCHASE_MOVIE_TIMEOUT:
                    self.setChatAbsolute(self.rng.choice(TTLocalizer.TF_STOREOWNER_TOOKTOOLONG), CFSpeech | CFTimeout)
                    self.resetClerk()
                else:
                    if mode == NPCToons.PURCHASE_MOVIE_COMPLETE:
                        self.setChatAbsolute(self.rng.choice(TTLocalizer.TF_STOREOWNER_GOODBYE), CFSpeech | CFTimeout)
                        self.resetClerk()
        return

    def popupPrizeGUI(self, task):
        self.accept(DONE_EVENT, self.__handleGuiDone)
        self.gui = ToonfestPrizeCollect.ToonfestPrizeCollect(npc=self, random=self.rng, doneEvent=DONE_EVENT)
        self.gui.show()
        return Task.done

    def __handleGuiDone(self):
        self.ignore(DONE_EVENT)
        self.d_requestFinished()
        self.gui = None
        return

    def requestPurchase(self, item, callback, optional=-1):
        blob = item.getBlob(store=CatalogItem.Customization)
        context = self.getCallbackContext(callback, [item])
        self.d_requestPrize(context, blob, optional)

    def d_requestPrize(self, context, blob, optional):
        self.sendUpdate('requestPrize', [context, blob, optional])

    def d_requestPrizeInfo(self, context, retcode):
        self.doCallbackContext(context, [retcode])

    def d_requestFinished(self):
        self.sendUpdate('requestFinished', [])