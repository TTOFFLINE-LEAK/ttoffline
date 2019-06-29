from DistributedNPCToon import *
from toontown.toonbase import TTLocalizer
from toontown.toon import LaughingManGlobals
import random

class DistributedNPCMagicCat(DistributedNPCToon):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedNPCMagicCat')

    def announceGenerate(self):
        DistributedNPCToon.announceGenerate(self)
        LaughingManGlobals.addToonEffect(self)

    def handleCollisionSphereEnter(self, collEntry):
        self.sendUpdate('avatarEnter', [])

    def handleInteract(self, avId):
        isLocalToon = avId == base.localAvatar.doId
        av = base.cr.doId2do.get(avId)
        if av is None:
            self.notify.warning('Avatar %d not found in doId' % avId)
            return
        if isLocalToon:
            self.getLockLocalToon().start()
            self.setupCamera(NPCToons.QUEST_MOVIE_INCOMPLETE)
        self.setupAvatars(av)
        fullString = TTLocalizer.MagicCatTalk
        self.acceptOnce(self.uniqueName('doneChatPage'), self.finishMovie, extraArgs=[av, isLocalToon])
        self.clearChat()
        self.setPageChat(avId, 0, fullString, 1)
        return

    def finishMovie(self, av, isLocalToon, elapsedTime):
        DistributedNPCToon.finishMovie(self, av, isLocalToon, elapsedTime)
        if isLocalToon:
            self.getFreeLocalToon().start()

    def setMovie(self, mode, npcId, avId, quests, timestamp):
        DistributedNPCToon.setMovie(self, mode, npcId, avId, quests, timestamp)
        isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.QUEST_MOVIE_TIMEOUT:
            if isLocalToon:
                self.getFreeLocalToon().start()

    def getLockLocalToon(self):
        return Sequence(Func(base.localAvatar.detachCamera), Func(base.localAvatar.setLocked, True), Func(base.localAvatar.stopTrackAnimToSpeed), Func(base.localAvatar.stopUpdateSmartCamera))

    def getFreeLocalToon(self):
        return Sequence(Func(base.localAvatar.attachCamera), Func(base.localAvatar.startTrackAnimToSpeed), Func(base.localAvatar.setLocked, False), Func(base.localAvatar.startUpdateSmartCamera))

    def setupAvatars(self, av):
        av.setZ(0)
        av.loop('neutral')
        DistributedNPCToonBase.setupAvatars(self, av)