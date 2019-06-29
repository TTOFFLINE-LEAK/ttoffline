from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedGoofySpeedwayAI import DistributedGoofySpeedwayAI
from toontown.toonbase import ToontownGlobals

class DistributedSuperGoofyAI(DistributedGoofySpeedwayAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuperGoofyAI')

    def walkSpeed(self):
        return ToontownGlobals.SuperGoofySpeed