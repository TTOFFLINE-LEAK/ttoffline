from direct.directnotify import DirectNotifyGlobal
from toontown.toon.DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from toontown.toonbase import TTLocalizer
import random

class DistributedNPCKongAI(DistributedNPCToonBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedNPCKongAI')

    def __init__(self, air, npcId, questCallback=None):
        DistributedNPCToonBaseAI.__init__(self, air, npcId, questCallback)
        self.available = 1

    def avatarEnter(self):
        if self.available:
            avId = self.air.getAvatarIdFromSender()
            DistributedNPCToonBaseAI.avatarEnter(self)
            self.notify.debug('avatar enter ' + str(avId))
            quote = random.choice(TTLocalizer.KongQuotes)
            quoteId = TTLocalizer.KongQuotes.index(quote)
            self.sendUpdate('handleInteract', [quoteId])
            self.available = 0
            taskMgr.doMethodLater(5.0, self.resetAvailable, self.taskName('reset-available-task'))

    def resetAvailable(self, task):
        self.available = 1
        return task.done