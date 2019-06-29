from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.interval.IntervalGlobal import *

class DistributedDGFlowerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDGFlowerAI')
    BASE_HEIGHT = 2.0
    MAX_HEIGHT = 10.0
    HEIGHT_PER_AV = 0.5

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.avatars = set()
        self.savedAvatars = None
        self.currentlyDooming = None
        self.height = 2.0
        return

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        self.avatars.add(avId)
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.handleAvatarLeave, extraArgs=[avId])
        self.adjustHeight()

    def avatarExit(self):
        avId = self.air.getAvatarIdFromSender()
        self.handleAvatarLeave(avId)

    def handleAvatarLeave(self, avId):
        self.ignore(self.air.getAvatarExitEvent(avId))
        if avId in self.avatars:
            self.avatars.remove(avId)
        self.adjustHeight()

    def adjustHeight(self):
        height = self.BASE_HEIGHT + self.HEIGHT_PER_AV * len(self.avatars)
        height = min(height, self.MAX_HEIGHT)
        self.b_setHeight(height, optional=False)

    def setHeight(self, height):
        self.height = height

    def d_setHeight(self, height, optional=False):
        self.sendUpdate('setHeight', [height, optional])

    def b_setHeight(self, height, optional=False):
        if not self.currentlyDooming:
            self.setHeight(height)
            if height == 10.0:
                optional = True
                height = 2.0
                self.savedAvatars = self.avatars
                self.currentlyDooming = True
                seq = Sequence(Wait(6.9), Func(self.doomToons), Func(self.notDooming)).start()
            self.d_setHeight(height, optional)

    def getHeight(self):
        return self.height

    def doomToons(self):
        for avatar in self.savedAvatars:
            toon = self.air.doId2do.get(avatar)
            toon.takeDamage(toon.hp)

    def notDooming(self):
        self.currentlyDooming = False