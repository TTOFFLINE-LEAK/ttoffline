from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectGlobal
from toontown.toon import NPCToons
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