from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedDistrictAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDistrictAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.name = None
        self.available = False
        self.full = False
        return

    def setName(self, name):
        self.name = name

    def d_setName(self, name):
        self.sendUpdate('setName', [name])

    def b_setName(self, name):
        self.setName(name)
        self.d_setName(name)

    def getName(self):
        return self.name

    def setAvailable(self, available):
        self.available = available

    def d_setAvilable(self, available):
        self.sendUpdate('setAvailable', [available])

    def b_setAvailable(self, available):
        self.setAvailable(available)
        self.d_setAvilable(available)

    def getAvailable(self):
        return self.available

    def setFull(self, full):
        self.full = full

    def d_setFull(self, full):
        self.sendUpdate('setFull', [full])

    def b_setFull(self, full):
        self.b_setAvailable(full)
        self.setFull(full)
        self.d_setFull(full)

    def getFull(self):
        return self.full