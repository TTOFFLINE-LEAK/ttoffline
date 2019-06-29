import random
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
import TreasureGlobals
from RegenTreasurePlannerAI import RegenTreasurePlannerAI
from DistributedTreasureAI import DistributedTreasureAI

class TFTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('TFTreasurePlannerAI')

    def __init__(self, zoneId, spawnPoints, spawnRate, maxTreasures):
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        self.treasureHoods = [ToontownGlobals.ToontownCentral, ToontownGlobals.DonaldsDock, ToontownGlobals.DaisyGardens, ToontownGlobals.TheBrrrgh, ToontownGlobals.MinniesMelodyland,
         ToontownGlobals.DonaldsDreamland, ToontownGlobals.OutdoorZone, ToontownGlobals.MyEstate]
        RegenTreasurePlannerAI.__init__(self, zoneId, None, 'SZTreasurePlanner-%d' % zoneId, spawnRate, maxTreasures)
        return

    def initSpawnPoints(self):
        pass

    def placeTreasure(self, index):
        spawnPoint = self.spawnPoints[index]
        hood = random.choice(self.treasureHoods)
        treasure = DistributedTreasureAI(simbase.air, self, TreasureGlobals.SafeZoneTreasureSpawns[hood][0], spawnPoint[0], spawnPoint[1], spawnPoint[2], TreasureGlobals.SafeZoneTreasureSpawns[hood][1])
        treasure.generateWithRequired(self.zoneId)
        self.treasures[index] = treasure

    def validAvatar(self, treasure, av):
        if av.getMaxHp() > av.getHp() > 0:
            av.toonUp(treasure.healAmount)
            return True
        return False