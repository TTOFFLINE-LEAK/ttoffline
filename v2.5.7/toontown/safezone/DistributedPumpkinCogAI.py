import datetime, time
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from toontown.toonbase import ToontownGlobals

class DistributedPumpkinCogAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPumpkinCogAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def giveRewardToAv(self):
        if not self.air:
            return
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            self.notify.warning('Invalid avatar requested pumpkin head!')
            return
        av = self.air.doId2do.get(avId)
        self.notify.info(('Avatar {0} requested pumpkin head').format(avId))
        now = datetime.datetime.now()
        endDate = datetime.datetime(now.year, 10, 31, 23, 59)
        if now > endDate:
            return
        deltaDate = endDate - now
        pumpkinTime = time.time() + deltaDate.days * 24 * 60 + deltaDate.seconds / 60
        av.b_setCheesyEffect(ToontownGlobals.CEPumpkin, 0, pumpkinTime)
        self.notify.info(('Avatar {0} now has a pumpkin head!').format(avId))