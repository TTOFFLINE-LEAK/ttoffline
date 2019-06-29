from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from panda3d.core import *

class GZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.GolfZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info("Creating zone... Chip 'n Dale's MiniGolf")
        HoodDataAI.HoodDataAI.startup(self)