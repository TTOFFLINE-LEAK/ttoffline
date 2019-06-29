from direct.directnotify import DirectNotifyGlobal
from toontown.catalog.CatalogItemList import CatalogItemList
from toontown.catalog.CatalogFurnitureItem import CatalogFurnitureItem
from toontown.catalog import CatalogItem
DNA2Furniture = {'house_interiorA': None, 
   'GardenA': None, 
   'chairA': 100, 
   'chair': 110, 
   'regular_bed': 200, 
   'FireplaceSq': 400, 
   'closetBoy': 500, 
   'lamp_short': 600, 
   'lamp_tall': 610, 
   'couch_1person': 700, 
   'couch_2person': 710, 
   'desk_only_wo_phone': 800, 
   'desk_only': 800, 
   'coatrack': 910, 
   'paper_trashcan': 920, 
   'rug': 1000, 
   'rugA': 1010, 
   'rugB': 1020, 
   'cabinetYwood': 1110, 
   'bookcase': 1120, 
   'bookcase_low': 1130, 
   'ending_table': 1200, 
   'jellybeanBank': 1300}

class DNAFurnitureReaderAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('DNAFurnitureReaderAI')

    def __init__(self, dnaData):
        self.dnaData = dnaData
        self.itemList = None
        return

    def buildList(self):
        self.itemList = CatalogItemList(store=CatalogItem.Customization | CatalogItem.Location)
        for i in xrange(self.dnaData.getNumChildren()):
            child = self.dnaData.at(i)
            if child.getName() == 'interior':
                interior = child
                break
        else:
            self.notify.error('Could not find "interior" in DNA!')

        for i in xrange(interior.getNumChildren()):
            child = interior.at(i)
            code = child.getCode()
            if code not in DNA2Furniture:
                self.notify.warning('Unrecognized furniture code %r!' % code)
                continue
            itemId = DNA2Furniture[code]
            if itemId is None:
                continue
            x, y, z = child.getPos()
            h, p, r = child.getHpr()
            self.itemList.append(CatalogFurnitureItem(itemId, posHpr=(
             x, y, z, h, p, r)))

        return

    def getList(self):
        if not self.itemList:
            self.buildList()
        return self.itemList

    def getBlob(self):
        return self.getList().getBlob()