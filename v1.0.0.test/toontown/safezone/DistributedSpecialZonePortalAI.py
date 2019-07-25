from direct.distributed import DistributedObjectAI
from direct.distributed import ClockDelta
from toontown.toonbase import ToontownGlobals
import random

class DistributedSpecialZonePortalAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.eligibleToons = []
        self.portalState = 0

    def delete(self):
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        self.accept('speedchat-phrase-said', self.handlePhrase)

    def togglePortal(self, state, avId, zoneId=0, npcId=0):
        if state == 0:
            taskMgr.doMethodLater(78.25, self.togglePortal, self.uniqueName('closePortal'), extraArgs=[
             1, avId, zoneId, npcId])
        else:
            if state == 2:
                npcId = random.choice(ToontownGlobals.MeetHereNpcIds)
                taskMgr.doMethodLater(5.517, self.setPortalState, self.uniqueName('setPortalState'), extraArgs=[2])
                taskMgr.doMethodLater(20.517, self.togglePortal, self.uniqueName('noResponse'), extraArgs=[
                 3, avId, zoneId, npcId])
            else:
                if state in (1, 3):
                    if state == 1:
                        time = 16.0
                    else:
                        time = 7.87
                    taskMgr.doMethodLater(time, self.setPortalState, self.uniqueName('setPortalState'), extraArgs=[0])
        self.sendUpdate('togglePortal', [state, zoneId, npcId, avId, ClockDelta.globalClockDelta.getRealNetworkTime()])

    def setPortalState(self, state):
        self.portalState = state

    def acceptPhrase(self):
        avId = self.air.getAvatarIdFromSender()
        self.eligibleToons.append(avId)
        avExitEvent = self.air.getAvatarExitEvent(avId)
        self.acceptOnce(avExitEvent, self.rejectPhraseById, [avId])

    def rejectPhrase(self):
        avId = self.air.getAvatarIdFromSender()
        self.rejectPhraseById(avId)

    def rejectPhraseById(self, avId):
        avExitEvent = self.air.getAvatarExitEvent(avId)
        self.ignore(avExitEvent)
        if avId not in self.eligibleToons:
            self.notify.warning(('Toon {} tried to stop being eligible to summon Meet Here Toon when they never were in the first place').format(avId))
        else:
            self.eligibleToons.remove(avId)

    def handlePhrase(self, avId, zoneId, phraseId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        if zoneId != self.zoneId or avId not in self.eligibleToons:
            return
        if phraseId == 1012 and not self.portalState:
            self.setPortalState(1)
            self.togglePortal(2, avId)
            return
        if phraseId not in ToontownGlobals.Phrase2Location.keys():
            return
        if self.portalState == 2:
            taskMgr.remove(self.uniqueName('noResponse'))
            zoneId = ToontownGlobals.Phrase2Location[phraseId]
            self.setPortalState(1)
            self.togglePortal(0, avId, zoneId)
            if zoneId == ToontownGlobals.ToontownOutskirts:
                av.b_setUnlocks([1])
                from toontown.hood.SpecialHoodDataAI import SpecialHoodDataAI
                for hood in simbase.air.hoods:
                    if isinstance(hood, SpecialHoodDataAI):
                        hood.specialZonePortal.togglePortal(0, avId, ToontownGlobals.ToontownCentral)