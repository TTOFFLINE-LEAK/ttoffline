from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectGlobal
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals
import json

class ModdingManager(DistributedObjectGlobal.DistributedObjectGlobal):
    notify = DirectNotifyGlobal.directNotify.newCategory('ModdingManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObjectGlobal.DistributedObjectGlobal.__init__(self, cr)
        cr.moddingManager = self
        self.colors = {}
        self.colorsLoaded = False
        self.cards = {}
        self.cardsLoaded = False
        self.defaultMaxToon = False
        self.defaultZone = ToontownGlobals.ToontownCentral

    def setColors(self, colors):
        colors = json.loads(colors)
        self.colors = colors

    def getColors(self):
        return self.colors

    def setCards(self, cards):
        cards = json.loads(cards)
        self.cards = cards

    def getCards(self):
        return self.cards

    def setDefaultMaxToon(self, state):
        self.defaultMaxToon = state

    def getDefaultMaxToon(self):
        return self.defaultMaxToon

    def setDefaultZone(self, zone):
        try:
            zone = ToontownGlobals.hood2Id[zone.upper()][0]
        except:
            zone = ToontownGlobals.ToontownCentral

        self.defaultZone = zone

    def getDefaultZone(self):
        return self.defaultZone