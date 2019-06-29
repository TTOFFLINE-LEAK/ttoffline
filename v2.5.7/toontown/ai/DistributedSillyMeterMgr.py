from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
import time

class DistributedSillyMeterMgr(DistributedObject.DistributedObject):
    neverDisable = 1
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSillyMeterMgr')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        cr.SillyMeterMgr = self
        self.curPhase = -1
        self.duration = -1
        self.isRunning = False

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.accept('SillyMeterRequestInfo', self.dispatchSillyMeterInfo)

    def delete(self):
        self.notify.debug('deleting SillyMetermgr')
        messenger.send('SillyMeterIsRunning', [False])
        DistributedObject.DistributedObject.delete(self)
        if hasattr(self.cr, 'SillyMeterMgr'):
            del self.cr.SillyMeterMgr

    def setCurPhase(self, newPhase):
        self.curPhase = newPhase
        messenger.send('SillyMeterPhase', [newPhase])

    def setIsRunning(self, isRunning):
        self.isRunning = isRunning
        messenger.send('SillyMeterIsRunning', [isRunning])

    def setCurPhaseDuration(self, duration):
        self.duration = duration
        messenger.send('SillyMeterDuration', [duration])

    def getCurPhaseDuration(self):
        return self.duration

    def setPhase(self, phase, duration):
        self.setIsRunning(phase >= 0)
        self.setCurPhase(phase)
        self.setCurPhaseDuration(duration)

    def dispatchSillyMeterInfo(self):
        messenger.send('SillyMeterIsRunning', [self.isRunning])
        messenger.send('SillyMeterPhase', [self.curPhase])
        messenger.send('SillyMeterDuration', [self.duration])