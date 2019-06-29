from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class ModdingManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('ModdingManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.colors = {}
        self.cards = {}

    def setColorsAiToUd(self, colors):
        self.colors = colors

    def getColors(self):
        return self.colors

    def setCardsAiToUd(self, cards):
        self.cards = cards

    def getCards(self):
        return self.cards