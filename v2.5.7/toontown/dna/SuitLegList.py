from DNASuitPoint import DNASuitPoint
from SuitLeg import SuitLeg

class SuitLegList:

    def __init__(self, path, dnaStore):
        self.path = path
        self.dnaStore = dnaStore
        self.legs = []
        self.add(self.path.getPoint(0), self.path.getPoint(1), self.getFirstLegType())
        for i in xrange(self.path.getNumPoints() - 1):
            pointA = self.path.getPoint(i)
            pointB = self.path.getPoint(i + 1)
            pointTypeA = pointA.getPointType()
            pointTypeB = pointB.getPointType()
            legType = self.getLegType(pointTypeA, pointTypeB)
            if pointTypeA == DNASuitPoint.COGHQ_OUT_POINT:
                self.add(pointA, pointB, SuitLeg.TFromCogHQ)
            self.add(pointA, pointB, legType)
            if pointTypeB == DNASuitPoint.COGHQ_IN_POINT:
                self.add(pointA, pointB, SuitLeg.TToCogHQ)

        numPoints = self.path.getNumPoints()
        pointA = self.path.getPoint(numPoints - 2)
        pointB = self.path.getPoint(numPoints - 1)
        self.add(pointA, pointB, self.getLastLegType())
        self.add(pointA, pointB, SuitLeg.TOff)

    def add(self, pointA, pointB, legType):
        zoneId = self.dnaStore.getSuitEdgeZone(pointA.getIndex(), pointB.getIndex())
        landmarkBuildingIndex = pointB.getLandmarkBuildingIndex()
        if landmarkBuildingIndex == -1:
            landmarkBuildingIndex = pointA.getLandmarkBuildingIndex()
        startTime = 0.0
        if len(self.legs) > 0:
            startTime = self.legs[(-1)].getEndTime()
        leg = SuitLeg(startTime, zoneId, landmarkBuildingIndex, pointA, pointB, legType)
        self.legs.append(leg)

    def getFirstLegType(self):
        if self.path.getPoint(0).getPointType() == DNASuitPoint.SIDE_DOOR_POINT:
            return SuitLeg.TFromSuitBuilding
        return SuitLeg.TFromSky

    def getLegType(self, pointTypeA, pointTypeB):
        if pointTypeA in (DNASuitPoint.FRONT_DOOR_POINT,
         DNASuitPoint.SIDE_DOOR_POINT):
            return SuitLeg.TWalkToStreet
        if pointTypeB in (DNASuitPoint.FRONT_DOOR_POINT,
         DNASuitPoint.SIDE_DOOR_POINT):
            return SuitLeg.TWalkFromStreet
        return SuitLeg.TWalk

    def getLastLegType(self):
        endPoint = self.path.getPoint(self.path.getNumPoints() - 1)
        endPointType = endPoint.getPointType()
        if endPointType == DNASuitPoint.FRONT_DOOR_POINT:
            return SuitLeg.TToToonBuilding
        if endPointType == DNASuitPoint.SIDE_DOOR_POINT:
            return SuitLeg.TToSuitBuilding
        return SuitLeg.TToSky

    def getNumLegs(self):
        return len(self.legs)

    def getLeg(self, index):
        return self.legs[index]

    def getType(self, index):
        return self.legs[index].getType()

    def getLegTime(self, index):
        return self.legs[index].getLegTime()

    def getZoneId(self, index):
        return self.legs[index].getZoneId()

    def getBlockNumber(self, index):
        return self.legs[index].getBlockNumber()

    def getPointA(self, index):
        return self.legs[index].getPointA()

    def getPointB(self, index):
        return self.legs[index].getPointB()

    def getStartTime(self, index):
        return self.legs[index].getStartTime()

    def getLegIndexAtTime(self, time, startLegIndex):
        for i, leg in enumerate(self.legs):
            if leg.getEndTime() > time:
                break

        return i

    def isPointInRange(self, point, lowTime, highTime):
        legIndex = self.getLegIndexAtTime(lowTime, 0)
        while legIndex < self.getNumLegs():
            leg = self.legs[legIndex]
            if leg.getEndTime() > highTime:
                break
            if leg.pointA == point or leg.pointB == point:
                return True
            legIndex += 1

        return False