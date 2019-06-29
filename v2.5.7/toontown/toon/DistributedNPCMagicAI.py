from panda3d.core import *
from DistributedNPCToonBaseAI import *
import NPCToons
from direct.task.Task import Task

class DistributedNPCMagicAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.busy = False

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        DistributedNPCToonBaseAI.avatarEnter(self)
        self.notify.debug('avatar enter ' + str(avId))
        if not self.busy:
            self.toggleTutorial('entered', avId)

    def toggleTutorial(self, state, avId):
        if state == 'entered':
            self.sendUpdate('doSequence', [avId])
            self.busy = True
        else:
            if state == 'exited':
                self.busy = False