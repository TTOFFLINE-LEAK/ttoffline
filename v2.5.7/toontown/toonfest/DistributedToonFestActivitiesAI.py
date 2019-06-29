from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toonfest.DistributedToonFestCannonAI import DistributedToonFestCannonAI
from toontown.toonfest.DistributedToonFestCannonActivityAI import DistributedToonFestCannonActivityAI
from toontown.toonfest.DistributedToonFestVictoryTrampolineActivityAI import DistributedToonFestVictoryTrampolineActivityAI

class DistributedToonFestActivitiesAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonFestActivitiesAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.cannonActivity = None
        return

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        if config.GetBool('want-toonfest-trampolines', True):
            self.spawnTrampolines()
        if config.GetBool('want-toonfest-cannons', True):
            self.spawnCannons()

    def spawnTrampolines(self):
        trampolinePos = [
         (117.207, -228.027, 5.39042, 0, 0, 0),
         (216.716, -223.989, 4.59702, 0, 0, 0),
         (75.665, -353.397, 8.33, 0, 0, 0),
         (370.043, -125.027, 9.63224, 0, 0, 0)]
        for i in trampolinePos:
            x, y, z, h, p, r = (
             i[0], i[1], i[2], i[3], i[4], i[5])
            trampoline = DistributedToonFestVictoryTrampolineActivityAI(self.air, self.doId, (0,
                                                                                              0,
                                                                                              0,
                                                                                              0))
            trampoline.generateWithRequired(self.zoneId)
            trampoline.sendUpdate('setX', [x])
            trampoline.sendUpdate('setY', [y])
            trampoline.sendUpdate('setZ', [z])
            trampoline.sendUpdate('setH', [h])
            trampoline.sendUpdate('setP', [p])
            trampoline.sendUpdate('setR', [r])

    def spawnCannons(self):
        cannonPos = [
         (123.081, -176.801, 5.88696, -90, 0, 0)]
        for i in cannonPos:
            x, y, z, h, p, r = (
             i[0], i[1], i[2], i[3], i[4], i[5])
            if not self.cannonActivity:
                self.cannonActivity = DistributedToonFestCannonActivityAI(self.air, self.doId, (0,
                                                                                                0,
                                                                                                0,
                                                                                                0), isTF=True)
                self.cannonActivity.generateWithRequired(self.zoneId)
            act = DistributedToonFestCannonAI(self.air, isTF=True)
            act.setActivityDoId(self.cannonActivity.doId)
            act.setPosHpr(x, y, z, h, 0, 0)
            act.generateWithRequired(self.zoneId)