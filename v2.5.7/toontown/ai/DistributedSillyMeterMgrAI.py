import datetime, time
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from toontown.toonbase import ToontownGlobals

class DistributedSillyMeterMgrAI(DistributedObjectAI.DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSillyMeterMgrAI')

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.curPhase = -1
        self.duration = -1

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        self.accept('SillyMeterRequestInfo', self.dispatchSillyMeterInfo)
        if self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLYMETER_HOLIDAY) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLYMETER_EXT_HOLIDAY):
            self.startSillyMeter()
        else:
            self.acceptOnce('holidayStart-%d' % ToontownGlobals.SILLYMETER_HOLIDAY, self.startSillyMeter)
            self.acceptOnce('holidayStart-%d' % ToontownGlobals.SILLYMETER_EXT_HOLIDAY, self.startSillyMeter)

    def startSillyMeter(self):
        self.ignore('holidayStart-%d' % ToontownGlobals.SILLYMETER_HOLIDAY)
        self.ignore('holidayStart-%d' % ToontownGlobals.SILLYMETER_EXT_HOLIDAY)
        now = datetime.datetime.now()
        endDate = datetime.datetime(now.year, 4, 5, 23, 59)
        if now > endDate:
            return
        deltaDate = endDate - now
        self.duration = deltaDate.days * 24 * 60 + deltaDate.seconds / 60
        nowTime = time.time()
        endTime = nowTime + self.duration
        self.curPhase = 6
        self.sendUpdate('setPhase', [self.curPhase, self.duration])
        self.acceptOnce('holidayEnd-%d' % ToontownGlobals.SILLYMETER_HOLIDAY, self.stopSillyMeter)
        self.acceptOnce('holidayEnd-%d' % ToontownGlobals.SILLYMETER_EXT_HOLIDAY, self.stopSillyMeter)

    def stopSillyMeter(self):
        self.ignore('holidayEnd-%d' % ToontownGlobals.SILLYMETER_HOLIDAY)
        self.ignore('holidayEnd-%d' % ToontownGlobals.SILLYMETER_EXT_HOLIDAY)
        self.curPhase = -1
        self.duration = -1
        self.sendUpdate('setPhase', [-1, -1])
        self.acceptOnce('holidayStart-%d' % ToontownGlobals.SILLYMETER_HOLIDAY, self.startSillyMeter)
        self.acceptOnce('holidayStart-%d' % ToontownGlobals.SILLYMETER_EXT_HOLIDAY, self.startSillyMeter)

    def getPhase(self):
        return (
         self.curPhase, self.duration)

    def getIsRunning(self):
        return self.curPhase >= 0

    def getCurPhase(self):
        return self.curPhase

    def dispatchSillyMeterInfo(self):
        messenger.send('SillyMeterPhase', [self.curPhase])