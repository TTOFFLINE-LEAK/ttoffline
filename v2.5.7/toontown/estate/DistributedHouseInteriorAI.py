from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from DistributedFurnitureManagerAI import *
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogWindowItem import CatalogWindowItem
from toontown.catalog.CatalogWallpaperItem import CatalogWallpaperItem
from toontown.catalog.CatalogMouldingItem import CatalogMouldingItem
from toontown.catalog.CatalogFlooringItem import CatalogFlooringItem
from toontown.catalog.CatalogWainscotingItem import CatalogWainscotingItem
from toontown.catalog.CatalogFurnitureItem import CatalogFurnitureItem
from toontown.dna.DNAStorage import DNAStorage
from DNAFurnitureReaderAI import DNAFurnitureReaderAI
from toontown.toonbase import ToontownGlobals
import HouseGlobals, random
houseInteriors = [
 'phase_5.5/dna/house_interior3.jazz',
 'phase_5.5/dna/house_interior4.jazz',
 'phase_5.5/dna/house_interior5.jazz',
 'phase_5.5/dna/house_interior7.jazz',
 'phase_5.5/dna/house_interior8.jazz',
 'phase_5.5/dna/house_interior10.jazz']
defaultWindows = [
 CatalogWindowItem(20, placement=2), CatalogWindowItem(20, placement=4)]
defaultWallpaper = [
 CatalogWallpaperItem(1110, 0, 1010, 0),
 CatalogMouldingItem(1000, 2),
 CatalogFlooringItem(1000, 4),
 CatalogWainscotingItem(1010, 4),
 CatalogWallpaperItem(1110, 0, 1010, 0),
 CatalogMouldingItem(1000, 2),
 CatalogFlooringItem(1000, 4),
 CatalogWainscotingItem(1010, 4)]

class DistributedHouseInteriorAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedHouseInteriorAI')

    def __init__(self, air, house):
        DistributedObjectAI.__init__(self, air)
        self.house = house
        self.houseId = 0
        self.houseIndex = 0
        self.wallpaper = ''
        self.windows = ''
        self.furnitureManager = DistributedFurnitureManagerAI(self.air, self.house, self)

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.furnitureManager.generateWithRequired(self.zoneId)

    def delete(self):
        DistributedObjectAI.delete(self)
        self.furnitureManager.delete()

    def initialize(self):
        dnaFile = houseInteriors[self.houseIndex]
        dnaStorage = DNAStorage()
        dnaData = simbase.air.loadDNAFileAI(dnaStorage, dnaFile)
        furnitureReader = DNAFurnitureReaderAI(dnaData)
        self.furnitureManager.setItems(furnitureReader.getBlob())
        items = furnitureReader.getList()
        items.append(CatalogFurnitureItem(1399, posHpr=(-11.5, 1.8, 0, 0, 0, 0)))
        self.furnitureManager.setItems(furnitureReader.getBlob())
        del self.furnitureManager.windows[:]
        self.furnitureManager.windows.extend(defaultWindows)
        self.furnitureManager.applyWindows()
        del self.furnitureManager.wallpaper[:]
        self.furnitureManager.wallpaper.extend(defaultWallpaper)
        self.furnitureManager.applyWallpaper()
        self.furnitureManager.saveToHouse()

    def setHouseId(self, houseId):
        self.houseId = houseId

    def d_setHouseId(self, houseId):
        self.sendUpdate('setHouseId', [houseId])

    def b_setHouseId(self, houseId):
        self.setHouseId(houseId)
        self.d_setHouseId(houseId)

    def getHouseId(self):
        return self.houseId

    def setHouseIndex(self, index):
        self.houseIndex = index

    def d_setHouseIndex(self, index):
        self.sendUpdate('setHouseIndex', [index])

    def b_setHouseIndex(self, index):
        self.setHouseIndex(index)
        self.d_setHouseIndex(index)

    def getHouseIndex(self):
        return self.houseIndex

    def setWallpaper(self, wallpaper):
        self.wallpaper = wallpaper

    def d_setWallpaper(self, wallpaper):
        self.sendUpdate('setWallpaper', [wallpaper])

    def b_setWallpaper(self, wallpaper):
        self.setWallpaper(wallpaper)
        if self.isGenerated():
            self.d_setWallpaper(wallpaper)

    def getWallpaper(self):
        return self.wallpaper

    def setWindows(self, windows):
        self.windows = windows

    def d_setWindows(self, windows):
        self.sendUpdate('setWindows', [windows])

    def b_setWindows(self, windows):
        self.setWindows(windows)
        if self.isGenerated():
            self.d_setWindows(windows)

    def getWindows(self):
        return self.windows