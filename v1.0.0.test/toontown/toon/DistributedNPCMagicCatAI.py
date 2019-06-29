from direct.directnotify import DirectNotifyGlobal
from toontown.toon.DistributedNPCToonAI import DistributedNPCToonAI

class DistributedNPCMagicCatAI(DistributedNPCToonAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedNPCMagicCatAI')

    def __init__(self, air, npcId, questCallback=None):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.busy:
            self.busy = avId
            self.notify.debug('avatar enter ' + str(avId))
            self.sendUpdate('handleInteract', [avId])
            taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))