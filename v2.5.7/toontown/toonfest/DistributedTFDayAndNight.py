from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObject import DistributedObject
from DayAndNightGlobals import *

class DistributedTFDayAndNight(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTFDayAndNight')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.cr = cr
        self.hood = base.cr.playGame.hood
        self.index = 0

    def generate(self):
        DistributedObject.generate(self)

    def setSky(self, index):
        self.notify.info('Setting sky: %s' % index)
        self.index = index
        if self.index == SUNRISE:
            self.loadSunrise()
        else:
            if self.index == MORNING:
                self.loadMorning()
            else:
                if self.index == SUNSET:
                    self.loadSunset()
                else:
                    if self.index == NIGHT:
                        self.loadNight()
                    else:
                        self.notify.warning('Tried to set a sky index that is invalid.')
                        self.setSky(index=0)
                        return

    def loadSunrise(self):
        self.hood.setSunrise()

    def loadMorning(self):
        self.hood.setMorning()

    def loadSunset(self):
        self.hood.setSunset()

    def loadNight(self):
        self.hood.setNight()