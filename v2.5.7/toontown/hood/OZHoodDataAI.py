from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from panda3d.core import *
from toontown.classicchars import DistributedChipAI, DistributedPoliceChipAI
from toontown.classicchars import DistributedDaleAI, DistributedJailbirdDaleAI
from toontown.distributed import DistributedTimerAI

class OZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.OutdoorZone
        if zoneId == None:
            zoneId = hoodId
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        self.notify.info("Creating zone... Chip 'n Dale's Acorn Acres")
        HoodDataAI.HoodDataAI.startup(self)
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-chip-and-dale', True):
                if simbase.air.config.GetBool('create-chip-and-dale', 1):
                    if self.air.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_COSTUMES):
                        chip = DistributedPoliceChipAI.DistributedPoliceChipAI(self.air)
                    else:
                        chip = DistributedChipAI.DistributedChipAI(self.air)
                    chip.generateWithRequired(self.zoneId)
                    chip.start()
                    self.addDistObj(chip)
                    if self.air.holidayManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_COSTUMES):
                        dale = DistributedJailbirdDaleAI.DistributedJailbirdDaleAI(self.air, chip.doId)
                    else:
                        dale = DistributedDaleAI.DistributedDaleAI(self.air, chip.doId)
                    dale.generateWithRequired(self.zoneId)
                    dale.start()
                    self.addDistObj(dale)
                    chip.setDaleId(dale.doId)
        self.timer = DistributedTimerAI.DistributedTimerAI(self.air)
        self.timer.generateWithRequired(self.zoneId)

    def cleanup(self):
        self.timer.delete()