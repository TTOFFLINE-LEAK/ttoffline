from direct.task.Task import Task
from panda3d.core import *
from DistributedNPCToonBaseAI import *
from toontown.quest import Quests
from random import randrange

class DistributedNPCSnowballGiverAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonBaseAI.__init__(self, air, npcId, questCallback)
        self.air = air

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        self.notify.debug('avatar enter ' + str(avId))
        if simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS) or simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.WINTER_CAROLING):
            av.b_setPieType(9)
            av.b_setNumPies(25)
        self.sendUpdate('gaveSnowballs', [self.npcId, avId, randrange(3)])