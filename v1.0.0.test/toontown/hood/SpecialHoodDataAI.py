from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.safezone import DistributedSpecialZonePortalAI
from toontown.safezone import DistributedPicnicBasketAI
from toontown.safezone import DistributedSafezoneJukeboxAI
from panda3d.core import *
from panda3d.toontown import *
import string

class SpecialHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SpecialHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.ToontownOutskirts
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        if config.GetBool('want-special-zone-portal', True):
            self.specialZonePortal = DistributedSpecialZonePortalAI.DistributedSpecialZonePortalAI(self.air)
            self.specialZonePortal.generateWithRequired(self.zoneId)
            self.addDistObj(self.specialZonePortal)
        self.safezoneJukebox = DistributedSafezoneJukeboxAI.DistributedSafezoneJukeboxAI(self.air)
        self.safezoneJukebox.generateWithRequired(self.zoneId)
        self.addDistObj(self.safezoneJukebox)
        self.createPicnicTables()

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