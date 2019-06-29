from direct.directnotify import DirectNotifyGlobal
import ZoneUtil
from toontown.building import DistributedBuildingMgrAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.safezone import ButterflyGlobals
from toontown.safezone import DistributedButterflyAI
from panda3d.core import *
from panda3d.toontown import *
from toontown.toon import NPCToons
from toontown.hood import DistributedPropGeneratorAI
from toontown.toonbase import ToontownGlobals, TTLocalizer

class HoodDataAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodDataAI')

    def __init__(self, air, zoneId, canonicalHoodId):
        self.air = air
        self.zoneId = zoneId
        self.canonicalHoodId = canonicalHoodId
        self.treasurePlanner = None
        self.buildingManagers = []
        self.suitPlanners = []
        self.propGenerators = []
        self.doId2do = {}
        self.replacementHood = None
        self.redirectingToMe = []
        self.hoodPopulation = 0
        self.pgPopulation = 0
        return

    def startup(self):
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            self.notify.info('Creating zone... %s' % self.getLocationName(zoneId))

        self.createFishingPonds()
        self.createPartyPeople()
        self.createBuildingManagers()
        self.createSuitPlanners()
        self.createPropGenerators()

    def shutdown(self):
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
        for propGenerator in self.propGenerators:
            del self.air.propGenerators[propGenerator.zoneId]

        self.propGenerators = []
        ButterflyGlobals.clearIndexes(self.zoneId)
        del self.fishingPonds
        for distObj in self.doId2do.values():
            distObj.requestDelete()

        del self.doId2do
        del self.air
        return

    def addDistObj(self, distObj):
        self.doId2do[distObj.doId] = distObj

    def removeDistObj(self, distObj):
        del self.doId2do[distObj.doId]

    def createPartyPeople(self):
        partyHats = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                foundPartyHats = self.air.findPartyHats(dnaData, zoneId)
                partyHats += foundPartyHats

        for distObj in partyHats:
            self.addDistObj(distObj)

        return

    def createFishingPonds(self):
        self.fishingPonds = []
        fishingPondGroups = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundFishingPonds, foundFishingPondGroups = self.air.findFishingPonds(dnaData, zoneId, area)
                self.fishingPonds += foundFishingPonds
                fishingPondGroups += foundFishingPondGroups

        for distObj in self.fishingPonds:
            self.addDistObj(distObj)
            npcs = NPCToons.createNpcsInZone(self.air, distObj.zoneId)
            for npc in npcs:
                self.addDistObj(npc)

        fishingSpots = []
        for dnaGroup, distPond in zip(fishingPondGroups, self.fishingPonds):
            fishingSpots += self.air.findFishingSpots(dnaGroup, distPond)

        for distObj in fishingSpots:
            self.addDistObj(distObj)

        classicFishingSpots = []
        for dnaGroup, distPond in zip(fishingPondGroups, self.fishingPonds):
            fishingSpots += self.air.findClassicFishingSpots(dnaGroup, distPond)

        for distObj in classicFishingSpots:
            self.addDistObj(distObj)

        return

    def createBuildingManagers(self):
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            if zone[1]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                dnaStore = self.air.dnaStoreMap[zone[0]]
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
                sp.initTasks()
                self.suitPlanners.append(sp)
                self.air.suitPlanners[zoneId] = sp

    def createButterflies(self, playground):
        ButterflyGlobals.generateIndexes(self.zoneId, playground)
        for i in xrange(0, ButterflyGlobals.NUM_BUTTERFLY_AREAS[playground]):
            for j in xrange(0, ButterflyGlobals.NUM_BUTTERFLIES[playground]):
                bfly = DistributedButterflyAI.DistributedButterflyAI(self.air, playground, i, self.zoneId)
                bfly.generateWithRequired(self.zoneId)
                bfly.start()
                self.addDistObj(bfly)

    def createPropGenerators(self):
        hoodIds = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            if self.zoneId < 30000:
                hoodIds.append(zone[0])

        for bldgMgr in self.buildingManagers:
            for block in bldgMgr.getBuildings():
                if hasattr(block, 'getExteriorAndInteriorZoneId'):
                    hoodIds.append(block.getExteriorAndInteriorZoneId()[1])

        for zoneId in hoodIds:
            propGenerator = DistributedPropGeneratorAI.DistributedPropGeneratorAI(self.air, zoneId)
            propGenerator.generateWithRequired(zoneId)
            self.addDistObj(propGenerator)
            self.propGenerators.append(propGenerator)
            self.air.propGenerators[zoneId] = propGenerator

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

    def getLocationName(self, zoneId, appendWelcomeValley=True):
        isWelcomeValley = False
        if ZoneUtil.isWelcomeValley(zoneId):
            isWelcomeValley = True
            zoneId = ZoneUtil.getTrueZoneId(zoneId, ToontownGlobals.ToontownCentral)
        lookupTable = ToontownGlobals.hoodNameMap
        isStreet = zoneId % 1000 != 0
        if isStreet:
            lookupTable = TTLocalizer.GlobalStreetNames
        name = lookupTable.get(zoneId, '')
        if isStreet:
            locationName = ('{0}, {1}').format(self.getLocationName(self.zoneId, False), name[2])
            if isWelcomeValley and appendWelcomeValley:
                locationName = locationName + ' (' + TTLocalizer.WelcomeValley[2] + ')'
            return locationName
        locationName = name[2]
        if isWelcomeValley and appendWelcomeValley:
            locationName = locationName + ' (' + TTLocalizer.WelcomeValley[2] + ')'
        return locationName