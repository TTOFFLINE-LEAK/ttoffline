from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.election import DistributedFlippyStandAI
from toontown.toonbase import ToontownGlobals
from toontown.toon import DistributedNPCFishermanAI
from toontown.toonfest import DistributedTFDayAndNightAI, DistributedToonfestBalloonAI, DistributedToonfestTowerBaseAI, DistributedQuizGameAI, DistributedDunkTankAI, BeanBagGlobals
from toontown.safezone import TreasureGlobals, TFTreasurePlannerAI, TFBeanBagPlannerAI
from toontown.toonfest.DayAndNightGlobals import TIME_OF_DAY_ZONES
from toontown.toonfest.DistributedToonFestActivitiesAI import DistributedToonFestActivitiesAI
from toontown.toon import NPCToons

class TFHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.ToonFest
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info('Creating zone... ToonFest')
        HoodDataAI.HoodDataAI.startup(self)
        tfBases = DistributedToonfestTowerBaseAI.DistributedToonfestTowerBaseAI(self.air)
        tfBases.generateWithRequired(self.zoneId)
        self.addDistObj(tfBases)
        stand = DistributedFlippyStandAI.DistributedFlippyStandAI(self.air)
        stand.generateWithRequired(self.zoneId)
        self.addDistObj(stand)
        if config.GetBool('want-toonfest-specials', True):
            self.quiz = DistributedQuizGameAI.DistributedQuizGameAI(self.air)
            self.quiz.generateWithRequired(self.zoneId)
            self.addDistObj(self.quiz)
            tank = DistributedDunkTankAI.DistributedDunkTankAI(self.air)
            tank.generateWithRequired(self.zoneId)
            self.addDistObj(tank)
        self.balloon = DistributedToonfestBalloonAI.DistributedToonfestBalloonAI(self.air)
        self.balloon.generateWithRequired(self.zoneId)
        self.balloon.b_setState('Waiting')
        self.addDistObj(self.balloon)
        for zone in TIME_OF_DAY_ZONES:
            dayCycle = DistributedTFDayAndNightAI.DistributedTFDayAndNightAI(self.air, zone)
            dayCycle.generateWithRequired(zone)
            self.addDistObj(dayCycle)

        self.tfActivities = DistributedToonFestActivitiesAI(self.air)
        self.tfActivities.generateWithRequired(self.zoneId)
        self.addDistObj(self.tfActivities)
        NPCToons.createNPC(self.air, 14500, NPCToons.NPCToonDict[14500], 7100, 0)

    def createTreasurePlanner(self):
        _, __, spawnPoints, spawnRate, maxTreasures = TreasureGlobals.SafeZoneTreasureSpawns[self.zoneId]
        self.treasurePlanner = TFTreasurePlannerAI.TFTreasurePlannerAI(self.zoneId, spawnPoints, spawnRate, maxTreasures)
        self.treasurePlanner.start()
        spawnPoints, spawnRate, maxTreasures = BeanBagGlobals.PlannerInfo
        self.beanBagPlanner = TFBeanBagPlannerAI.TFBeanBagPlannerAI(self.zoneId, spawnPoints, spawnRate, maxTreasures)
        self.beanBagPlanner.start()