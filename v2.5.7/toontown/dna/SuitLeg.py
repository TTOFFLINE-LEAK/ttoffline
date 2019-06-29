from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals

class SuitLeg:
    TWalkFromStreet = 0
    TWalkToStreet = 1
    TWalk = 2
    TFromSky = 3
    TToSky = 4
    TFromSuitBuilding = 5
    TToSuitBuilding = 6
    TToToonBuilding = 7
    TFromCogHQ = 8
    TToCogHQ = 9
    TOff = 10
    TypeToName = {TWalkFromStreet: 'WalkFromStreet', 
       TWalkToStreet: 'WalkToStreet', 
       TWalk: 'Walk', 
       TFromSky: 'FromSky', 
       TToSky: 'ToSky', 
       TFromSuitBuilding: 'FromSuitBuilding', 
       TToSuitBuilding: 'ToSuitBuilding', 
       TToToonBuilding: 'ToToonBuilding', 
       TFromCogHQ: 'FromCogHQ', 
       TToCogHQ: 'ToCogHQ', 
       TOff: 'Off'}

    def __init__(self, startTime, zoneId, blockNumber, pointA, pointB, type):
        self.startTime = startTime
        self.zoneId = zoneId
        self.blockNumber = blockNumber
        self.pointA = pointA
        self.pointB = pointB
        self.type = type
        self.posA = self.pointA.getPos()
        self.posB = self.pointB.getPos()
        distance = (self.posB - self.posA).length()
        self.legTime = distance / ToontownGlobals.SuitWalkSpeed
        self.endTime = self.startTime + self.getLegTime()

    def getStartTime(self):
        return self.startTime

    def getZoneId(self):
        return self.zoneId

    def getBlockNumber(self):
        return self.blockNumber

    def getPointA(self):
        return self.pointA

    def getPointB(self):
        return self.pointB

    def getType(self):
        return self.type

    def getPosA(self):
        return self.posA

    def getPosB(self):
        return self.posB

    def getLegTime(self):
        if self.type in (SuitLeg.TWalk, SuitLeg.TWalkFromStreet,
         SuitLeg.TWalkToStreet):
            return self.legTime
        if self.type == SuitLeg.TFromSky:
            return SuitTimings.fromSky
        if self.type == SuitLeg.TToSky:
            return SuitTimings.toSky
        if self.type == SuitLeg.TFromSuitBuilding:
            return SuitTimings.fromSuitBuilding
        if self.type == SuitLeg.TToSuitBuilding:
            return SuitTimings.toSuitBuilding
        if self.type in (SuitLeg.TToToonBuilding, SuitLeg.TToCogHQ,
         SuitLeg.TFromCogHQ):
            return SuitTimings.toToonBuilding
        return 0.0

    def getEndTime(self):
        return self.endTime

    def getPosAtTime(self, time):
        if self.type in (SuitLeg.TFromSky, SuitLeg.TFromSuitBuilding,
         SuitLeg.TFromCogHQ):
            return self.posA
        if self.type in (SuitLeg.TToSky, SuitLeg.TToSuitBuilding,
         SuitLeg.TToToonBuilding, SuitLeg.TToCogHQ,
         SuitLeg.TOff):
            return self.posB
        delta = self.posB - self.posA
        return self.posA + delta * (time / self.getLegTime())

    def getTypeName(self):
        if self.type in SuitLeg.TypeToName:
            return SuitLeg.TypeToName[self.type]
        return '**invalid**'