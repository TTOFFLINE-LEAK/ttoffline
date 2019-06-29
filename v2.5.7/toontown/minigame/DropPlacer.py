from direct.showbase.RandomNumGen import RandomNumGen
import CatchGameGlobals, DropScheduler
from toontown.parties.PartyGlobals import CatchActivityDuration as PartyCatchDuration

class DropPlacer():

    def __init__(self, game, numPlayers, dropTypes, startTime=None):
        self.game = game
        self.numPlayers = numPlayers
        self.dropTypes = dropTypes
        self.dtIndex = 0
        self._createScheduler(startTime)
        self._createRng()

    def _createScheduler(self, startTime):
        self.scheduler = DropScheduler.DropScheduler(CatchGameGlobals.GameDuration, self.game.FirstDropDelay, self.game.DropPeriod, self.game.MaxDropDuration, self.game.FasterDropDelay, self.game.FasterDropPeriodMult, startTime=startTime)

    def _createRng(self):
        self.rng = self.game.randomNumGen

    def skipPercent(self, percent):
        numSkips = self.scheduler.skipPercent(percent)
        self.dtIndex += numSkips
        return numSkips

    def doneDropping(self, continuous=None):
        return self.scheduler.doneDropping(continuous)

    def getDuration(self):
        return self.scheduler.getDuration()

    def getT(self):
        return self.scheduler.getT()

    def stepT(self):
        self.scheduler.stepT()

    def getNextDropTypeName(self):
        if self.dtIndex >= len(self.dropTypes):
            self.game.notify.debug('warning: defaulting to anvil')
            typeName = 'anvil'
        else:
            typeName = self.dropTypes[self.dtIndex]
        self.dtIndex += 1
        return typeName

    def getRandomColRow(self):
        col = self.rng.randrange(0, self.game.DropColumns)
        row = self.rng.randrange(0, self.game.DropRows)
        return [
         col, row]

    def getNextDrop(self):
        raise RuntimeError, 'DropPlacer.getNextDrop should never be called'


class RandomDropPlacer(DropPlacer):

    def __init__(self, game, numPlayers, dropTypes, startTime=None):
        DropPlacer.__init__(self, game, numPlayers, dropTypes, startTime=startTime)

    def getNextDrop(self):
        col, row = self.getRandomColRow()
        drop = [self.getT(), self.getNextDropTypeName(), [col, row]]
        self.stepT()
        return drop


class RegionDropPlacer(DropPlacer):
    DropRegionTables = [
     [
      [
       1,
       1,
       2,
       3,
       3],
      [
       1,
       1,
       2,
       3,
       3],
      [
       0,
       1,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       3,
       4]],
     [
      [
       1,
       2,
       2,
       3,
       3,
       4],
      [
       1,
       1,
       2,
       3,
       4,
       4],
      [
       1,
       1,
       2,
       3,
       4,
       4],
      [
       0,
       1,
       2,
       3,
       4,
       5],
      [
       0,
       1,
       2,
       3,
       4,
       5],
      [
       0,
       1,
       2,
       3,
       4,
       5]],
     [
      [
       1,
       1,
       2,
       2,
       2,
       3,
       3],
      [
       1,
       1,
       2,
       2,
       2,
       3,
       3],
      [
       0,
       1,
       2,
       2,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       2,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       2,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       2,
       2,
       3,
       4],
      [
       0,
       1,
       2,
       2,
       2,
       3,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       6,
       3,
       4,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       8,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       8,
       6,
       3,
       4,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       8,
       8,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       8,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       8,
       8,
       6,
       3,
       4,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       8,
       10,
       9,
       6,
       3,
       4,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       10,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       8,
       10,
       10,
       9,
       6,
       3,
       4,
       4]],
     [
      [
       1,
       2,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       7,
       3],
      [
       1,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       3],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       1,
       2,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       7,
       3,
       4],
      [
       0,
       0,
       1,
       5,
       8,
       10,
       11,
       12,
       9,
       6,
       3,
       4,
       4]]]
    Players2dropTable = [DropRegionTables[0],
     DropRegionTables[0],
     DropRegionTables[0],
     DropRegionTables[1],
     DropRegionTables[1],
     DropRegionTables[2],
     DropRegionTables[3],
     DropRegionTables[3],
     DropRegionTables[4],
     DropRegionTables[4],
     DropRegionTables[5],
     DropRegionTables[5],
     DropRegionTables[5],
     DropRegionTables[6],
     DropRegionTables[6],
     DropRegionTables[7],
     DropRegionTables[7],
     DropRegionTables[7],
     DropRegionTables[8],
     DropRegionTables[8]]

    @classmethod
    def getDropRegionTable(cls, numPlayers):
        return cls.Players2dropTable[min(len(cls.Players2dropTable) - 1, numPlayers)]

    def __init__(self, game, numPlayers, dropTypes, startTime=None):
        DropPlacer.__init__(self, game, numPlayers, dropTypes, startTime=startTime)
        self.DropRegionTable = self.getDropRegionTable(self.numPlayers)
        self.DropRegion2GridCoordList = {}
        for row in range(len(self.DropRegionTable)):
            rowList = self.DropRegionTable[row]
            for column in range(len(rowList)):
                region = rowList[column]
                if not self.DropRegion2GridCoordList.has_key(region):
                    self.DropRegion2GridCoordList[region] = []
                self.DropRegion2GridCoordList[region].append([row, column])

        self.DropRegions = self.DropRegion2GridCoordList.keys()
        self.DropRegions.sort()
        self.emptyDropRegions = self.DropRegions[:]
        self.fallingObjs = []

    def getNextDrop(self):
        t = self.getT()
        while len(self.fallingObjs):
            landTime, dropRegion = self.fallingObjs[0]
            if landTime > t:
                break
            self.fallingObjs = self.fallingObjs[1:]
            if dropRegion not in self.emptyDropRegions:
                self.emptyDropRegions.append(dropRegion)

        candidates = self.emptyDropRegions
        if len(candidates) == 0:
            candidates = self.DropRegions
        dropRegion = self.rng.choice(candidates)
        row, col = self.rng.choice(self.DropRegion2GridCoordList[dropRegion])
        dropTypeName = self.getNextDropTypeName()
        drop = [t, dropTypeName, [row, col]]
        duration = self.game.BaselineDropDuration
        self.fallingObjs.append([t + duration, dropRegion])
        if dropRegion in self.emptyDropRegions:
            self.emptyDropRegions.remove(dropRegion)
        self.stepT()
        return drop


class PartyRegionDropPlacer(RegionDropPlacer):

    def __init__(self, game, numPlayers, generationId, dropTypes, startTime=None):
        self.generationId = generationId
        RegionDropPlacer.__init__(self, game, numPlayers, dropTypes, startTime=startTime)

    def _createRng(self):
        self.rng = RandomNumGen(self.generationId + self.game.doId)

    def _createScheduler(self, startTime):
        self.scheduler = DropScheduler.ThreePhaseDropScheduler(PartyCatchDuration, self.game.FirstDropDelay, self.game.DropPeriod, self.game.MaxDropDuration, self.game.SlowerDropPeriodMult, self.game.NormalDropDelay, self.game.FasterDropDelay, self.game.FasterDropPeriodMult, startTime=startTime)


class PathDropPlacer(DropPlacer):

    def __init__(self, game, numPlayers, dropTypes, startTime=None):
        DropPlacer.__init__(self, game, numPlayers, dropTypes, startTime=startTime)
        self.moves = [[0, -1],
         [
          1, -1],
         [
          1, 0],
         [
          1, 1],
         [
          0, 1],
         [
          -1, 1],
         [
          -1, 0],
         [
          -1, -1]]
        self.paths = []
        for i in xrange(self.numPlayers):
            dir = self.rng.randrange(0, len(self.moves))
            col, row = self.getRandomColRow()
            path = {'direction': dir, 'location': [
                          col, row]}
            self.paths.append(path)

        self.curPathIndex = 0

    def getValidDirection(self, col, row, dir):
        redirectTop = [
         (6, 2),
         2,
         2,
         3,
         4,
         5,
         6,
         6]
        redirectRight = [0,
         0,
         (0, 4),
         4,
         4,
         5,
         6,
         7]
        redirectBottom = [0,
         1,
         2,
         2,
         (2, 6),
         6,
         6,
         7]
        redirectLeft = [0,
         1,
         2,
         3,
         4,
         4,
         (4, 0),
         0]
        redirectTopRight = [6,
         (6, 4),
         4,
         4,
         4,
         5,
         6,
         6]
        redirectBottomRight = [0,
         0,
         0,
         (0, 6),
         6,
         6,
         6,
         7]
        redirectBottomLeft = [0,
         1,
         2,
         2,
         2,
         (2, 0),
         0,
         0]
        redirectTopLeft = [2,
         2,
         2,
         3,
         4,
         4,
         4,
         (4, 2)]
        tables = [None,
         redirectTop,
         redirectBottom,
         None,
         redirectLeft,
         redirectTopLeft,
         redirectBottomLeft,
         None,
         redirectRight,
         redirectTopRight,
         redirectBottomRight]
        if col == 0:
            colIndex = 1
        else:
            if col == self.game.DropColumns - 1:
                colIndex = 2
            else:
                colIndex = 0
        if row == 0:
            rowIndex = 1
        else:
            if row == self.game.DropRows - 1:
                rowIndex = 2
            else:
                rowIndex = 0
        index = (colIndex << 2) + rowIndex
        redirectTable = tables[index]
        if not redirectTable:
            return dir
        newDir = redirectTable[dir]
        if type(newDir) != type(1):
            newDir = self.rng.choice(newDir)
        return newDir

    def getNextDrop(self):
        path = self.paths[self.curPathIndex]
        col, row = path['location']
        dir = path['direction']
        turns = [-1,
         0,
         0,
         1]
        turn = self.rng.choice(turns)
        if turn:
            dir = (dir + turn) % len(self.moves)
        dir = self.getValidDirection(col, row, dir)
        dCol, dRow = self.moves[dir]
        col += dCol
        row += dRow
        col = min(max(col, 0), self.game.DropColumns - 1)
        row = min(max(row, 0), self.game.DropRows - 1)
        path['location'] = [col, row]
        path['direction'] = dir
        self.curPathIndex = (self.curPathIndex + 1) % len(self.paths)
        drop = [self.getT(), self.getNextDropTypeName(), [col, row]]
        self.stepT()
        return drop