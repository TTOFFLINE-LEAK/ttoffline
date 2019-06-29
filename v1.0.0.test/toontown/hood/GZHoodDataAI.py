from direct.directnotify import DirectNotifyGlobal
import HoodDataAI, ZoneUtil
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from panda3d.toontown import *
from toontown.safezone import DistributedGolfKartAI
import string

class GZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GZHoodDataAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.GolfZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        self.createGolfKarts()

    def cleanup(self):
        pass

    def findAndCreateGolfKarts(self, dnaGroup, zoneId, area, overrideDNAZone=0, type='golf_kart'):
        golfKarts = []
        golfKartGroups = []
        if isinstance(dnaGroup, DNAGroup) and string.find(dnaGroup.getName(), type) >= 0:
            golfKartGroups.append(dnaGroup)
            if type == 'golf_kart':
                nameInfo = dnaGroup.getName().split('_')
                golfCourse = int(nameInfo[2])
                pos = Point3(0, 0, 0)
                hpr = Point3(0, 0, 0)
                for i in xrange(dnaGroup.getNumChildren()):
                    childDnaGroup = dnaGroup.at(i)
                    if string.find(childDnaGroup.getName(), 'starting_block') >= 0:
                        padLocation = dnaGroup.getName().split('_')[2]
                        pos = childDnaGroup.getPos()
                        hpr = childDnaGroup.getHpr()
                        break

                pos += Point3(0, 0, 0.05)
                golfKart = DistributedGolfKartAI.DistributedGolfKartAI(self.air, golfCourse, pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
            else:
                self.notify.warning('unhandled case')
            golfKart.generateWithRequired(zoneId)
            golfKarts.append(golfKart)
        else:
            if isinstance(dnaGroup, DNAVisGroup) and not overrideDNAZone:
                zoneId = ZoneUtil.getTrueZoneId(int(dnaGroup.getName().split(':')[0]), zoneId)
            for i in xrange(dnaGroup.getNumChildren()):
                childGolfKarts, childGolfKartGroups = self.findAndCreateGolfKarts(dnaGroup.at(i), zoneId, area, overrideDNAZone, type)
                golfKarts += childGolfKarts
                golfKartGroups += childGolfKartGroups

        return (golfKarts, golfKartGroups)

    def createGolfKarts(self):
        self.golfKarts = []
        self.golfKartGroups = []
        for zone in self.air.zoneTable[self.canonicalHoodId]:
            zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
            dnaData = self.air.dnaDataMap.get(zone[0], None)
            if isinstance(dnaData, DNAData):
                area = ZoneUtil.getCanonicalZoneId(zoneId)
                foundKarts, foundKartGroups = self.findAndCreateGolfKarts(dnaData, zoneId, area, overrideDNAZone=True)
                self.golfKarts += foundKarts
                self.golfKartGroups += foundKartGroups

        for golfKart in self.golfKarts:
            golfKart.start()
            self.addDistObj(golfKart)

        return