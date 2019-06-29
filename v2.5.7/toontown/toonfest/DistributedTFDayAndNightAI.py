from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.interval.IntervalGlobal import *
from DayAndNightGlobals import *

class DistributedTFDayAndNightAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTFDayAndNightAI')

    def __init__(self, air, zone):
        DistributedObjectAI.__init__(self, air)
        self.air = air
        self.zoneId = zone
        self.index = 0
        self.timeOfDaySequence = None
        return

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.setTimerTask()

    def getSky(self, index):
        self.index = index

    def setTimerTask(self):
        self.timeOfDaySequence = Sequence(Func(self.setSunRise), Wait(SUNRISE_TIME), Func(self.setMorning), Wait(DAY_TIME), Func(self.setSunset), Wait(SUNSET_TIME), Func(self.setNight), Wait(NIGHT_TIME))
        self.timeOfDaySequence.loop()

    def setMorning(self):
        self.sendSetSky(index=MORNING)

    def setSunset(self):
        self.sendSetSky(index=SUNSET)

    def setNight(self):
        self.sendSetSky(index=NIGHT)

    def setSunRise(self):
        self.sendSetSky(index=SUNRISE)

    def sendSetSky(self, index):
        if index not in LIST_OF_TOD_STAGES:
            self.notify.warning('Tried to send the client a sky index that was invalid.')
            self.air.writeServerEvent('suspicious', issue='Tried to send the client a sky index that was invalid.')
            self.sendSetSky(index=0)
            return
        if index == SUNRISE:
            self.loadSunrise()
        else:
            if index == MORNING:
                self.loadMorning()
            else:
                if index == SUNSET:
                    self.loadSunset()
                else:
                    if index == NIGHT:
                        self.loadNight()
        self.sendUpdate('setSky', [index])

    def loadSunrise(self):
        self.sendUpdate('loadSunrise', [])

    def loadMorning(self):
        self.sendUpdate('loadMorning', [])

    def loadSunset(self):
        self.sendUpdate('loadSunset', [])

    def loadNight(self):
        self.sendUpdate('loadNight', [])

    def delete(self):
        DistributedObjectAI.delete(self)
        self.cleanup()

    def disable(self):
        DistributedObjectAI.disable(self)
        self.cleanup()

    def cleanup(self):
        if self.timeOfDaySequence:
            if self.timeOfDaySequence.isPlaying():
                self.timeOfDaySequence.finish()
            self.timeOfDaySequence = None
            del self.timeOfDaySequence
        return