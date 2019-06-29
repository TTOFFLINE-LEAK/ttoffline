from direct.distributed import DistributedObjectAI
from direct.interval.IntervalGlobal import *
HEIGHT_DELTA = 0.5
MAX_HEIGHT = 10.0
MIN_HEIGHT = 2.0
EASTER_EGG_COOLDOWN = 900.0

class DistributedDGFlowerAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.height = MIN_HEIGHT
        self.avList = []
        self.easterEggAvatarIds = []
        self.easterEggActivated = False
        self.easterEggCooldown = False
        return

    def delete(self):
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def start(self):
        return

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.avList:
            self.avList.append(avId)
            if self.height + HEIGHT_DELTA <= MAX_HEIGHT:
                self.height += HEIGHT_DELTA
                self.b_setHeight(self.height)

    def avatarExit(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.avList:
            self.avList.remove(avId)
            if self.height - HEIGHT_DELTA >= MIN_HEIGHT:
                self.height -= HEIGHT_DELTA
                self.b_setHeight(self.height)

    def setHeight(self, height):
        self.height = height

    def d_setHeight(self, height):
        self.sendUpdate('setHeight', [height])

    def b_setHeight(self, height):
        if not self.easterEggActivated:
            self.setHeight(height)
            if height == MAX_HEIGHT and not self.easterEggCooldown:
                height = MIN_HEIGHT
                self.easterEggAvatarIds = self.avList[:]
                self.easterEggActivated = True
                seq = Sequence(Wait(7.5), Func(self.activateEasterEgg), Func(self.deactivateEasterEgg)).start()
                self.d_activateEasterEgg(self.easterEggAvatarIds)
            self.d_setHeight(height)

    def activateEasterEgg(self):
        for avId in self.easterEggAvatarIds:
            toon = self.air.doId2do.get(avId)
            if toon:
                hp = toon.hp
                if hp < 1:
                    hp = 1
                toon.takeDamage(hp)

    def d_activateEasterEgg(self, avIds):
        self.sendUpdate('activateEasterEgg', [avIds])

    def deactivateEasterEgg(self):
        self.easterEggAvatarIds = []
        self.easterEggActivated = False
        self.easterEggCooldown = True
        taskMgr.doMethodLater(EASTER_EGG_COOLDOWN, self.resetEasterEgg, self.taskName('easter-egg-reset'), extraArgs=[])

    def resetEasterEgg(self):
        self.easterEggCooldown = False