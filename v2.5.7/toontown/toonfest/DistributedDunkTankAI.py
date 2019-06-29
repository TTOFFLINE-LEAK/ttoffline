from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from direct.task import Task
REWARD_AMT = 5

class DistributedDunkTankAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDunkTank')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.isAvailable = True

    def b_setAvailable(self, avail):
        self.d_setAvailable(avail)
        self.setAvailable(avail)

    def d_setAvailable(self, avail):
        self.sendUpdate('setAvailable', [avail])

    def setAvailable(self, avail):
        self.isAvailable = avail

    def getAvailable(self):
        return self.isAvailable

    def hitTarget(self):
        if not self.isAvailable:
            return
        self.b_setAvailable(False)
        avId = self.air.getAvatarIdFromSender()
        self.d_dunk()
        taskMgr.doMethodLater(12, self.rewardAvAndReset, self.taskName('dunk-reward-av'), extraArgs=[avId])

    def d_dunk(self):
        self.sendUpdate('dunk', [])

    def rewardAvAndReset(self, avId):
        self.b_setAvailable(True)
        av = self.air.doId2do.get(avId)
        if av is None:
            return
        av.addTokens(REWARD_AMT)
        self.sendUpdateToAvatarId(avId, 'rewardAv', [])
        return Task.done