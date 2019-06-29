from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
import ZoneUtil
from toontown.building import DistributedBuildingMgrAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.safezone import ButterflyGlobals
from toontown.safezone import DistributedButterflyAI
from toontown.safezone import TreasureGlobals
from toontown.safezone.SZTreasurePlannerAI import SZTreasurePlannerAI
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.dna.DNASpawnerAI import *

class HoodDataAI(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodDataAI')

    def __init__(self, air, zoneId, canonicalHoodId):
        self.air = air
        self.zoneId = zoneId
        DirectObject.DirectObject.__init__(self)
        self.canonicalHoodId = canonicalHoodId
        self.treasurePlanner = None
        self.buildingManagers = []
        self.suitPlanners = []
        self.doId2do = {}
        self.replacementHood = None
        self.redirectingToMe = []
        self.hoodPopulation = 0
        self.pgPopulation = 0
        self.classicChar = None
        try:
            self.cCharClass
        except:
            self.cCharClass = None
        else:
            try:
                self.cCharClassAF
            except:
                self.cCharClassAF = None
            else:
                try:
                    self.cCharClassHW
                except:
                    self.cCharClassHW = None

            try:
                self.cCharConfigVar
            except:
                self.cCharConfigVar = 'want-classic-chars'

        self.startup()
        return

    def startup(self):
        self.createTreasurePlanner()
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            if zone[1]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                DNASpawnerAI().spawnObjects(self.air.genDNAFileName(zoneId), zoneId)

        self.createBuildingManagers()
        self.createSuitPlanners()
        if self.cCharClass != None:
            if simbase.air.holidayManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES) and self.cCharClassAF != None:
                self.createAFClassicCharacter()
            else:
                self.createClassicCharacter()
        return

    def shutdown(self):
        self.ignore('holidayStart-%d' % ToontownGlobals.APRIL_FOOLS_COSTUMES)
        self.ignore('holidayEnd-%d' % ToontownGlobals.APRIL_FOOLS_COSTUMES)
        self.setRedirect(None)
        if self.treasurePlanner:
            self.treasurePlanner.stop()
            self.treasurePlanner.deleteAllTreasuresNow()
            self.treasurePlanner = None
        for suitPlanner in self.suitPlanners:
            suitPlanner.requestDelete()
            del self.air.suitPlanners[suitPlanner.zoneId]

        self.suitPlanners = []
        for buildingManager in self.buildingManagers:
            buildingManager.cleanup()
            del self.air.buildingManagers[buildingManager.branchID]

        self.buildingManagers = []
        ButterflyGlobals.clearIndexes(self.zoneId)
        for distObj in self.doId2do.values():
            distObj.requestDelete()

        del self.doId2do
        del self.air
        return

    def addDistObj(self, distObj):
        self.doId2do[distObj.doId] = distObj

    def removeDistObj(self, distObj):
        del self.doId2do[distObj.doId]

    def createTreasurePlanner(self):
        if self.zoneId in (8000, 17000, 11000, 12000, 13000, 10000, 1002000, 19000,
                           62000):
            return
        treasureType, healAmount, spawnPoints, spawnRate, maxTreasures = TreasureGlobals.SafeZoneTreasureSpawns[self.zoneId]
        self.treasurePlanner = SZTreasurePlannerAI(self.zoneId, treasureType, healAmount, spawnPoints, spawnRate, maxTreasures)
        self.treasurePlanner.start()

    def createBuildingManagers(self):
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            if zone[1]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                dnaStore = self.air.dnaStoreMap(zone[0])
                mgr = DistributedBuildingMgrAI.DistributedBuildingMgrAI(self.air, zoneId, dnaStore, self.air.trophyMgr)
                self.buildingManagers.append(mgr)
                self.air.buildingManagers[zoneId] = mgr

    def createSuitPlanners(self):
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            if zone[2]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                sp = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, zoneId)
                sp.generateWithRequired(zoneId)
                sp.d_setZoneId(zoneId)
                if zoneId != ToontownGlobals.OldOakStreet:
                    sp.initTasks()
                self.suitPlanners.append(sp)
                self.air.suitPlanners[zoneId] = sp

    def createButterflies(self, playground):
        ButterflyGlobals.generateIndexes(self.zoneId, playground)
        for i in range(0, ButterflyGlobals.NUM_BUTTERFLY_AREAS[playground]):
            for j in range(0, ButterflyGlobals.NUM_BUTTERFLIES[playground]):
                bfly = DistributedButterflyAI.DistributedButterflyAI(self.air, playground, i, self.zoneId)
                bfly.generateWithRequired(self.zoneId)
                bfly.start()
                self.addDistObj(bfly)

    def createClassicCharacter(self):
        if self.classicChar:
            self.classicChar.requestDelete()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool(self.cCharConfigVar, True):
                if self.air.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_COSTUMES) and self.cCharClassHW:
                    self.classicChar = self.cCharClassHW(self.air)
                else:
                    self.classicChar = self.cCharClass(self.air)
                self.classicChar.generateWithRequired(self.zoneId)
                self.classicChar.start()
                self.addDistObj(self.classicChar)
                if self.cCharClassAF != None:
                    self.acceptOnce('holidayStart-%d' % ToontownGlobals.APRIL_FOOLS_COSTUMES, self.createAFClassicCharacter)
        return

    def createAFClassicCharacter(self):
        self.ignore('holidayStart-%d' % ToontownGlobals.APRIL_FOOLS_COSTUMES)
        if self.classicChar:
            self.classicChar.requestDelete()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool(self.cCharConfigVar, True):
                self.classicChar = self.cCharClassAF(self.air)
                self.classicChar.generateWithRequired(self.zoneId)
                self.classicChar.start()
                self.addDistObj(self.classicChar)
                self.acceptOnce('holidayEnd-%d' % ToontownGlobals.APRIL_FOOLS_COSTUMES, self.createClassicCharacter)

    def setRedirect(self, replacementHood):
        if self.replacementHood:
            self.replacementHood[0].redirectingToMe.remove(self)
        self.replacementHood = replacementHood
        if self.replacementHood:
            self.replacementHood[0].redirectingToMe.append(self)

    def hasRedirect(self):
        return self.replacementHood != None

    def getRedirect(self):
        if self.replacementHood == None:
            return self
        return self.replacementHood[0].getRedirect()
        return

    def incrementPopulation(self, zoneId, increment):
        self.hoodPopulation += increment
        if ZoneUtil.isPlayground(zoneId):
            self.pgPopulation += increment

    def getHoodPopulation(self):
        population = self.hoodPopulation
        for hood in self.redirectingToMe:
            population += hood.getHoodPopulation()

        return population

    def getPgPopulation(self):
        population = self.pgPopulation
        for pg in self.redirectingToMe:
            population += pg.getPgPopulation()

        return population