from direct.distributed import DistributedObjectAI
from direct.directnotify import DirectNotifyGlobal
from direct.task.Task import Task

class DistributedPresentAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPresentAI')

    def __init__(self, air, x, y, z, h, p, r, model):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.air = air
        self.posHpr = (x, y, z, h, p, r)
        self.model = model
        self.isUnavailable = False

    def getPosHpr(self):
        return self.posHpr

    def getModelId(self):
        return self.model

    def giveReward(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if self.isUnavailable:
            self.notify.warning('avId %s tried to take a present while it was unavailable!' % avId)
            return
        if av:
            av.addMoney(100)
            self.b_setUnavailable(True)
            taskMgr.doMethodLater(120, self.makeAvailable, self.uniqueName('makeAvailable'))
        else:
            self.notify.warning('avId %s does not exist, but tried to take a present' % avId)

    def makeAvailable(self, task):
        self.b_setUnavailable(False)
        return Task.done

    def getUnavailable(self):
        return self.isUnavailable

    def b_setUnavailable(self, avail):
        self.d_setUnavailable(avail)
        self.setUnavailable(avail)

    def d_setUnavailable(self, avail):
        self.sendUpdate('setUnavailable', [avail])

    def setUnavailable(self, avail):
        self.isUnavailable = avail