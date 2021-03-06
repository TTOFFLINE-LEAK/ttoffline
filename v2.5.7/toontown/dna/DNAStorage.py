from DNAError import DNAError
from DNASuitEdge import DNASuitEdge
from DNASuitPath import DNASuitPath
from DNASuitPoint import DNASuitPoint

class DNAStorage:

    def __init__(self):
        self.suitPoints = []
        self.suitPointMap = {}
        self.DNAGroups = {}
        self.DNAVisGroups = []
        self.suitEdges = {}
        self.battleCells = []
        self.nodes = {}
        self.hoodNodes = {}
        self.placeNodes = {}
        self.fonts = {}
        self.blockTitles = {}
        self.blockArticles = {}
        self.blockBuildingTypes = {}
        self.blockDoors = {}
        self.blockNumbers = []
        self.blockZones = {}
        self.textures = {}
        self.catalogCodes = {}

    def getSuitPath(self, startPoint, endPoint, minPathLen=40, maxPathLen=300):
        path = DNASuitPath()
        path.addPoint(startPoint)
        while path.getNumPoints() < maxPathLen:
            startPointIndex = startPoint.getIndex()
            if startPointIndex == endPoint.getIndex():
                if path.getNumPoints() >= minPathLen:
                    break
            if startPointIndex not in self.suitEdges:
                raise DNAError('Could not find DNASuitPath.')
            edges = self.suitEdges[startPointIndex]
            for edge in edges:
                startPoint = edge.getEndPoint()
                startPointType = startPoint.getPointType()
                if startPointType != DNASuitPoint.FRONT_DOOR_POINT:
                    if startPointType != DNASuitPoint.SIDE_DOOR_POINT:
                        break
            else:
                raise DNAError('Could not find DNASuitPath.')

            path.addPoint(startPoint)

        return path

    def getSuitEdgeTravelTime(self, startIndex, endIndex, suitWalkSpeed):
        startPoint = self.suitPointMap.get(startIndex)
        endPoint = self.suitPointMap.get(endIndex)
        if not startPoint or not endPoint:
            return 0.0
        distance = (endPoint.getPos() - startPoint.getPos()).length()
        return distance / suitWalkSpeed

    def getSuitEdgeZone(self, startIndex, endIndex):
        return self.getSuitEdge(startIndex, endIndex).getZoneId()

    def getAdjacentPoints(self, point):
        path = DNASuitPath()
        startIndex = point.getIndex()
        if startIndex not in self.suitEdges:
            return path
        for edge in self.suitEdges[startIndex]:
            path.addPoint(edge.getEndPoint())

        return path

    def storeSuitPoint(self, suitPoint):
        if not isinstance(suitPoint, DNASuitPoint):
            raise TypeError('suitPoint must be an instance of DNASuitPoint')
        self.suitPoints.append(suitPoint)
        self.suitPointMap[suitPoint.getIndex()] = suitPoint

    def getSuitPointAtIndex(self, index):
        return self.suitPoints[index]

    def getSuitPointWithIndex(self, index):
        return self.suitPointMap.get(index)

    def resetSuitPoints(self):
        self.suitPoints = []
        self.suitPointMap = {}
        self.suitEdges = {}

    def resetTextures(self):
        self.textures = {}

    def resetHood(self):
        self.resetBlockNumbers()

    def findDNAGroup(self, node):
        return self.DNAGroups[node]

    def removeDNAGroup(self, dnagroup):
        for node, group in self.DNAGroups.items():
            if group == dnagroup:
                del self.DNAGroups[node]

    def resetDNAGroups(self):
        self.DNAGroups = {}

    def getNumDNAVisGroups(self):
        return len(self.DNAVisGroups)

    def getDNAVisGroupName(self, i):
        return self.DNAVisGroups[i].getName()

    def storeDNAVisGroup(self, group):
        self.DNAVisGroups.append(group)

    def storeSuitEdge(self, startIndex, endIndex, zoneId):
        startPoint = self.getSuitPointWithIndex(startIndex)
        endPoint = self.getSuitPointWithIndex(endIndex)
        edge = DNASuitEdge(startPoint, endPoint, zoneId)
        self.suitEdges.setdefault(startIndex, []).append(edge)
        return edge

    def getSuitEdge(self, startIndex, endIndex):
        edges = self.suitEdges[startIndex]
        for edge in edges:
            if edge.getEndPoint().getIndex() == endIndex:
                return edge

    def removeBattleCell(self, cell):
        self.battleCells.remove(cell)

    def storeBattleCell(self, cell):
        self.battleCells.append(cell)

    def resetBattleCells(self):
        self.battleCells = []

    def findNode(self, code):
        if code in self.nodes:
            return self.nodes[code]
        if code in self.hoodNodes:
            return self.hoodNodes[code]
        if code in self.placeNodes:
            return self.placeNodes[code]

    def resetNodes(self):
        for node in self.nodes:
            self.nodes[node].removeNode()

        self.nodes = {}

    def resetHoodNodes(self):
        for node in self.hoodNodes:
            self.hoodNodes[node].removeNode()

        self.hoodNodes = {}

    def resetPlaceNodes(self):
        for node in self.placeNodes:
            self.placeNodes[node].removeNode()

        self.placeNodes = {}

    def storeNode(self, node, code):
        self.nodes[code] = node

    def storeHoodNode(self, node, code):
        self.hoodNodes[code] = node

    def storePlaceNode(self, node, code):
        self.placeNodes[code] = node

    def findFont(self, code):
        if code in self.fonts:
            return self.fonts[code]

    def resetFonts(self):
        self.fonts = {}

    def storeFont(self, font, code):
        self.fonts[code] = font

    def getBlock(self, name):
        block = name[name.find(':') - 2:name.find(':')]
        if not block[0].isdigit():
            block = block[1:]
        return block

    def getBlockBuildingType(self, blockNumber):
        if blockNumber in self.blockBuildingTypes:
            return self.blockBuildingTypes[blockNumber]

    def getTitleFromBlockNumber(self, blockNumber):
        if blockNumber in self.blockTitles:
            return self.blockTitles[blockNumber]
        return ''

    def getDoorPosHprFromBlockNumber(self, blockNumber):
        key = str(blockNumber)
        if key in self.blockDoors:
            return self.blockDoors[key]

    def storeBlockDoor(self, blockNumber, door):
        self.blockDoors[str(blockNumber)] = door

    def storeBlockTitle(self, blockNumber, title):
        self.blockTitles[blockNumber] = title

    def storeBlockArticle(self, blockNumber, article):
        self.blockArticles[blockNumber] = article

    def storeBlockBuildingType(self, blockNumber, buildingType):
        self.blockBuildingTypes[blockNumber] = buildingType

    def storeBlock(self, blockNumber, title, article, bldgType, zoneId):
        self.storeBlockNumber(blockNumber)
        self.storeBlockTitle(blockNumber, title)
        self.storeBlockArticle(blockNumber, article)
        self.storeBlockBuildingType(blockNumber, bldgType)
        self.storeBlockZone(blockNumber, zoneId)

    def storeTexture(self, name, texture):
        self.textures[name] = texture

    def resetDNAVisGroups(self):
        self.DNAVisGroups = []

    def resetDNAVisGroupsAI(self):
        self.resetDNAVisGroups()

    def getNumDNAVisGroupsAI(self):
        return self.getNumDNAVisGroups()

    def getNumSuitPoints(self):
        return len(self.suitPoints)

    def getNumVisiblesInDNAVisGroup(self, i):
        return self.DNAVisGroups[i].getNumVisibles()

    def getVisibleName(self, i, j):
        return self.DNAVisGroups[i].getVisibleName(j)

    def getDNAVisGroupAI(self, i):
        return self.DNAVisGroups[i]

    def storeCatalogCode(self, category, code):
        if category not in self.catalogCodes:
            self.catalogCodes[category] = []
        self.catalogCodes[category].append(code)

    def getNumCatalogCodes(self, category):
        if category not in self.catalogCodes:
            return -1
        return len(self.catalogCodes[category])

    def resetCatalogCodes(self):
        self.catalogCodes = {}

    def getCatalogCode(self, category, index):
        return self.catalogCodes[category][index]

    def findTexture(self, name):
        if name in self.textures:
            return self.textures[name]

    def discoverContinuity(self):
        return 1

    def resetBlockNumbers(self):
        self.blockNumbers = []
        self.blockZones = {}
        self.blockArticles = {}
        self.resetBlockDoors()
        self.blockTitles = {}
        self.blockBuildingTypes = {}

    def getNumBlockNumbers(self):
        return len(self.blockNumbers)

    def storeBlockNumber(self, blockNumber):
        self.blockNumbers.append(blockNumber)

    def getBlockNumberAt(self, index):
        return self.blockNumbers[index]

    def getZoneFromBlockNumber(self, blockNumber):
        if blockNumber in self.blockZones:
            return self.blockZones[blockNumber]

    def storeBlockZone(self, blockNumber, zoneId):
        self.blockZones[blockNumber] = zoneId

    def resetBlockZones(self):
        self.blockZones = {}

    def resetBlockDoors(self):
        self.blockDoors = {}

    def cleanup(self):
        self.resetBattleCells()
        self.resetBlockNumbers()
        self.resetDNAGroups()
        self.resetDNAVisGroups()
        self.resetDNAVisGroupsAI()
        self.resetFonts()
        self.resetHood()
        self.resetHoodNodes()
        self.resetNodes()
        self.resetPlaceNodes()
        self.resetSuitPoints()
        self.resetTextures()
        self.resetCatalogCodes()
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()