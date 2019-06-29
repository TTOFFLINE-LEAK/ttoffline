from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedMickeyAI import DistributedMickeyAI
from toontown.toonbase import ToontownGlobals

class DistributedWitchMinnieAI(DistributedMickeyAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedWitchMinnieAI')

    def walkSpeed(self):
        return ToontownGlobals.WitchMinnieSpeed