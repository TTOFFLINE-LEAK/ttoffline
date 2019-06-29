from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from toontown.toonbase import ToontownGlobals

class DistributedTTCHQEventMgrAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTTCHQEventMgrAI')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.stinkCounter = 0
        self.stinkyToons = []
        self.decrementCounterTaskName = 'decrement-counter-{}'

    def delete(self):
        self.ignoreAll()
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        self.accept('speedchat-phrase-said', self.handlePhrase)

    def incrementStinkCounter(self):
        self.stinkCounter += 1
        if self.stinkCounter >= ToontownGlobals.HQEventStinkThreshold:
            for x in xrange(self.stinkCounter, 0, -1):
                taskMgr.remove(self.decrementCounterTaskName.format(x))

            self.stinkCounter = 0
            self.sendUpdate('die', [])
        taskMgr.doMethodLater(ToontownGlobals.HQEventStinkLifetime, self.decrementStinkCounter, self.decrementCounterTaskName.format(self.stinkCounter))

    def decrementStinkCounter(self, task):
        self.stinkCounter = max(self.stinkCounter - 1, 0)
        return task.done

    def acceptStink(self):
        avId = self.air.getAvatarIdFromSender()
        self.stinkyToons.append(avId)
        avExitEvent = self.air.getAvatarExitEvent(avId)
        self.acceptOnce(avExitEvent, self.rejectStinkById, [avId])

    def rejectStink(self):
        avId = self.air.getAvatarIdFromSender()
        self.rejectStinkById(avId)

    def rejectStinkById(self, avId):
        avExitEvent = self.air.getAvatarExitEvent(avId)
        self.ignore(avExitEvent)
        if avId not in self.stinkyToons:
            self.notify.warning(('Toon {} tried to stop being eligible to stink HQ when they never were in the first place').format(avId))
        else:
            self.stinkyToons.remove(avId)

    def handlePhrase(self, avId, zoneId, phraseId):
        if zoneId != self.zoneId or avId not in self.stinkyToons or phraseId != 905:
            return
        self.incrementStinkCounter()