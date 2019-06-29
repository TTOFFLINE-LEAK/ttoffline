from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedPlutoAI import DistributedPlutoAI
from toontown.toonbase import ToontownGlobals

class DistributedWesternPlutoAI(DistributedPlutoAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedWesternPlutoAI')

    def walkSpeed(self):
        return ToontownGlobals.WesternPlutoSpeed