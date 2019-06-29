from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedDonaldAI import DistributedDonaldAI
from toontown.toonbase import ToontownGlobals

class DistributedFrankenDonaldAI(DistributedDonaldAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedFrankenDonaldAI')

    def walkSpeed(self):
        return ToontownGlobals.FrankenDonaldSpeed