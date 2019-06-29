from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedMickeyAI import DistributedMickeyAI
from toontown.toonbase import ToontownGlobals

class DistributedVampireMickeyAI(DistributedMickeyAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVampireMickeyAI')

    def walkSpeed(self):
        return ToontownGlobals.VampireMickeySpeed