import random
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.toontown import *
from toontown.catalog import CatalogItem
from toontown.catalog.CatalogFlooringItem import CatalogFlooringItem
from toontown.catalog.CatalogFurnitureItem import CatalogFurnitureItem
from toontown.catalog.CatalogItemList import CatalogItemList
from toontown.catalog.CatalogMouldingItem import CatalogMouldingItem
from toontown.catalog.CatalogWainscotingItem import CatalogWainscotingItem
from toontown.catalog.CatalogWallpaperItem import CatalogWallpaperItem
from toontown.catalog.CatalogWindowItem import CatalogWindowItem
from toontown.estate import HouseGlobals
from toontown.estate.DistributedFurnitureManagerAI import DistributedFurnitureManagerAI
code2furnitureId = {'regular_bed': 200, 
   'closetBoy': 500, 
   'jellybeanBank': 1350, 
   'FireplaceSq': 400, 
   'chairA': 100, 
   'cabinetYwood': 110, 
   'couch_1person': 700, 
   'rug': 1000, 
   'rugA': 1010, 
   'rugB': 1020, 
   'couch_2person': 710, 
   'ending_table': 1200, 
   'lamp_short': 600, 
   'lamp_tall': 610, 
   'phone': 1399, 
   'desk_only_wo_phone': 800, 
   'desk_only': 800}
defaultWindows = CatalogItemList([
 CatalogWindowItem(20, 2),
 CatalogWindowItem(20, 4)], store=CatalogItem.WindowPlacement)
defaultWallpaper = CatalogItemList([
 CatalogWallpaperItem(1110, 0, 1010, 0),
 CatalogMouldingItem(1000, 2),
 CatalogFlooringItem(1000, 4),
 CatalogWainscotingItem(1010, 4),
 CatalogWallpaperItem(1110, 0, 1010, 0),
 CatalogMouldingItem(1000, 2),
 CatalogFlooringItem(1000, 4),
 CatalogWainscotingItem(1010, 4)], store=CatalogItem.Customization)

class DistributedHouseInteriorAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedHouseInteriorAI')

    def __init__(self, air, house):
        DistributedObjectAI.__init__(self, air)
        self.house = house
        self.houseId = 0
        self.houseIndex = 0
        self.wallpaper = ''
        self.windows = ''
        self.gender = None
        self.furnitureManager = None
        self.houseInterior = None
        self.dnaData = None
        self.dnaStore = DNAStorage()
        return

    def setHouseId(self, houseId):
        self.houseId = houseId

    def d_setHouseId(self, houseId):
        self.sendUpdate('setHouseId', [houseId])

    def b_setHouseId(self, houseId):
        self.setHouseId(houseId)
        self.d_setHouseId(houseId)

    def getHouseId(self):
        return self.houseId

    def setHouseIndex(self, houseIndex):
        self.houseIndex = houseIndex

    def d_setHouseIndex(self, houseIndex):
        self.sendUpdate('setHouseIndex', [houseIndex])

    def b_setHouseIndex(self, houseIndex):
        self.setHouseIndex(houseIndex)
        self.d_setHouseIndex(houseIndex)

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

    def start(self):
        if self.house.getAvatarId() == 0:
            return
        self.furnitureManager = DistributedFurnitureManagerAI(self.air, self.house, self)
        self.furnitureManager.setOwnerId(self.house.getAvatarId())
        self.furnitureManager.setOwnerName(self.house.getName())
        self.furnitureManager.setInteriorId(self.doId)
        self.furnitureManager.generateWithRequired(self.zoneId)
        if self.furnitureManager.getNumItems() == 0:
            self.createInterior()
        else:
            self.furnitureManager.loadFurniture()

    def createInterior(self):
        self.houseInterior = random.choice(HouseGlobals.interiors)
        self.dnaData = self.air.loadDNAFileAI(self.dnaStore, self.houseInterior[0])
        furnitureData = {}
        for i in xrange(self.dnaData.getNumChildren()):
            node = self.dnaData.at(i)
            if node.getName() == 'interior':
                for j in xrange(node.getNumChildren()):
                    obj = node.at(j)
                    objName = obj.getName()
                    x, y, z = obj.getPos()
                    h, p, r = obj.getHpr()
                    code = obj.getCode()
                    furnitureData[objName] = {'code': code, 
                       'posHpr': (
                                x, y, z, h, 0, 0), 
                       'scale': obj.getScale(), 
                       'itemId': code2furnitureId.get(code, 0)}

        furnitureData['phone'] = {'code': 'phone', 'posHpr': (-11, 2, 0, 0, 0, 0), 
           'scale': 'phone', 
           'itemId': code2furnitureId.get('phone', 0)}
        interiorItems = CatalogItemList(store=CatalogItem.Customization | CatalogItem.Location)
        ignoredItems = ['house_interiorA_DNARoot', 'GardenA_DNARoot']
        for name, data in furnitureData.iteritems():
            itemId = data.get('itemId', 0)
            if itemId == 0:
                if name not in ignoredItems:
                    self.notify.warning('Tried to generate item %s but the ID was not found!' % name)
                continue
            if name == 'closetBoy_DNARoot' and self.gender == 'f':
                itemId += 10
            newItem = CatalogFurnitureItem(itemId, posHpr=data.get('posHpr'))
            interiorItems.append(newItem)

        self.house.b_setInteriorItems(interiorItems.getBlob())
        self.house.b_setInteriorWindows(defaultWindows.getBlob())
        self.house.b_setInteriorWallpaper(defaultWallpaper.getBlob())
        self.furnitureManager.wallpaper = self.house.interiorWallpaper
        self.furnitureManager.windows = self.house.interiorWindows
        self.furnitureManager.loadFurniture()
        self.furnitureManager.saveFurniture()