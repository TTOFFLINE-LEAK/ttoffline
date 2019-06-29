from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.parties import PartyGlobals, PartyUtils

class DistributedPartyActivityAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyActivityAI')

    def __init__(self, air, parent, activityTuple):
        DistributedObjectAI.__init__(self, air)
        self.parent = parent
        x, y, h = activityTuple[1:]
        self.x = PartyUtils.convertDistanceFromPartyGrid(x, 0)
        self.y = PartyUtils.convertDistanceFromPartyGrid(y, 1)
        self.z = 0
        self.h = h * PartyGlobals.PartyGridHeadingConverter
        self.p = 0
        self.r = 0
        self.toonsPlaying = []

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getZ(self):
        return self.z

    def getH(self):
        return self.h

    def getP(self):
        return self.p

    def getR(self):
        return self.r

    def getPartyDoId(self):
        return self.parent

    def updateToonsPlaying(self):
        self.sendUpdate('setToonsPlaying', [self.toonsPlaying])

    def toonJoinRequest(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.air.writeServerEvent('suspicious', avId, 'tried to enter activity from another shard!')
            return
        self.toonsPlaying.append(avId)
        self.updateToonsPlaying()

    def toonExitRequest(self):
        avId = self.air.getAvatarIdFromSender()
        self.toonsPlaying.remove(avId)
        self.updateToonsPlaying()

    def toonExitDemand(self):
        self.toonExitRequest()

    def toonReady(self):
        pass