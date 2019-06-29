import random
from direct.directnotify import DirectNotifyGlobal
from toontown.toonfest import DistributedBeanBagAI, BeanBagGlobals
from RegenTreasurePlannerAI import RegenTreasurePlannerAI

class TFBeanBagPlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('TFBeanBagPlannerAI')

    def __init__(self, zoneId, spawnPoints, spawnRate, maxTreasures):
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        RegenTreasurePlannerAI.__init__(self, zoneId, 0, 'TFBeanBagPlannerAI-%d' % zoneId, spawnRate, maxTreasures)

    def initSpawnPoints(self):
        pass

    def placeTreasure(self, index):
        spawnPoint = self.spawnPoints[index]
        value = random.choice(BeanBagGlobals.Value2Texture.keys())
        bag = DistributedBeanBagAI.DistributedBeanBagAI(simbase.air, self, spawnPoint[0], spawnPoint[1], spawnPoint[2], value)
        bag.generateWithRequired(self.zoneId)
        self.treasures[index] = bag

    def validAvatar(self, treasure, av):
        if treasure.value == BeanBagGlobals.TOKEN_BAG:
            av.addTokens(treasure.value)
        else:
            av.addMoney(treasure.value)
        return True