from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.safezone import OZTreasurePlannerAI
from panda3d.core import *
from panda3d.toontown import *
from toontown.safezone import DistributedPicnicBasketAI
from toontown.classicchars import DistributedChipAI
from toontown.classicchars import DistributedDaleAI
from toontown.distributed import DistributedTimerAI
import string
from toontown.safezone import DistributedPicnicTableAI
from toontown.safezone import DistributedChineseCheckersAI
from toontown.safezone import DistributedCheckersAI

class OZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('OZHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.OutdoorZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        self.classicChars = []
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        if simbase.air.config.GetBool('create-chip-and-dale', 1):
            chip = DistributedChipAI.DistributedChipAI(self.air)
            chip.generateWithRequired(self.zoneId)
            chip.start()
            self.addDistObj(chip)
            self.classicChars.append(chip)
            dale = DistributedDaleAI.DistributedDaleAI(self.air, chip.doId)
            dale.generateWithRequired(self.zoneId)
            dale.start()
            self.addDistObj(dale)
            self.classicChars.append(dale)
            chip.setDaleId(dale.doId)
        self.treasurePlanner = OZTreasurePlannerAI.OZTreasurePlannerAI(self.zoneId)
        self.treasurePlanner.start()
        self.timer = DistributedTimerAI.DistributedTimerAI(self.air)
        self.timer.generateWithRequired(self.zoneId)
        self.createPicnicTables()
        if simbase.config.GetBool('want-game-tables', 0):
            self.createGameTables()

    def cleanup(self):
        self.timer.delete()

    def findAndCreateGameTables(self, dnaGroup, zoneId, area, overrideDNAZone=0, type='game_table'):
        picnicTables = []
        picnicTableGroups = []
        if isinstance(dnaGroup, DNAGroup) and string.find(dnaGroup.getName(), type) >= 0:
            if type == 'game_table':
                nameInfo = dnaGroup.getName().split('_')
                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in xrange(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    if string.find(childDnaGroup.getName(), 'game_table') >= 0:
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                picnicTable = DistributedPicnicTableAI.DistributedPicnicTableAI(self.air, zoneId, nameInfo[2], pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                picnicTables.append(picnicTable)
        else:
            if isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone:
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in xrange(dnaGroup.getNumChildren()):
                childPicnicTables = self.findAndCreateGameTables(dnaGroup.at(i), zoneId, area, overrideDNAZone, type)
                picnicTables += childPicnicTables

        return picnicTables

    def findAndCreatePicnicTables(self, dnaGroup, zoneId, area, overrideDNAZone=0, type='picnic_table'):
        picnicTables = []
        picnicTableGroups = []
        if isinstance(dnaGroup, DNAGroup) and string.find(dnaGroup.getName(), type) >= 0:
            if type == 'picnic_table':
                nameInfo = dnaGroup.getName().split('_')
                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in xrange(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    if string.find(childDnaGroup.getName(), 'picnic_table') >= 0:
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                picnicTable = DistributedPicnicBasketAI.DistributedPicnicBasketAI(self.air, nameInfo[2], pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
                picnicTable.generateWithRequired(zoneId)
                picnicTables.append(picnicTable)
        else:
            if isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone:
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in xrange(dnaGroup.getNumChildren()):
                childPicnicTables = self.findAndCreatePicnicTables(dnaGroup.at(i), zoneId, area, overrideDNAZone, type)
                picnicTables += childPicnicTables

        return picnicTables

    def createGameTables(self):
        self.gameTables = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundTables = self.findAndCreateGameTables(dnaData, zoneId, area, overrideDNAZone=True)
                self.gameTables += foundTables

        for picnicTable in self.gameTables:
            self.addDistObj(picnicTable)

        return

    def createPicnicTables(self):
        self.picnicTables = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundTables = self.findAndCreatePicnicTables(dnaData, zoneId, area, overrideDNAZone=True)
                self.picnicTables += foundTables

        for picnicTable in self.picnicTables:
            picnicTable.start()
            self.addDistObj(picnicTable)

        return