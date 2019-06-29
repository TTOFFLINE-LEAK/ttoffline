from direct.distributed import DistributedObject
from direct.distributed.ClockDelta import *
from direct.task.Task import Task
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
ChangeDirectionDebounce = 1.0
ChangeDirectionTime = 1.0

class DistributedToonfestTowerBase(DistributedObject.DistributedObject):

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.spinStartTime = 0.0
        self.rpm = 5.0
        self.degreesPerSecond = self.rpm / 60.0 * 360.0
        self.offset = 0.0
        self.oldOffset = 0.0
        self.lerpStart = 0.0
        self.lerpFinish = 1.0
        self.speedUpSound = None
        self.changeDirectionSound = None
        self.lastChangeDirection = 0.0
        return

    def generate(self):
        self.base1 = base.cr.playGame.hood.loader.base1
        self.base2 = base.cr.playGame.hood.loader.base2
        self.base3 = base.cr.playGame.hood.loader.base3
        base.cr.parentMgr.registerParent(ToontownGlobals.SPToonfestTower1, self.base1)
        base.cr.parentMgr.registerParent(ToontownGlobals.SPToonfestTower2, self.base2)
        base.cr.parentMgr.registerParent(ToontownGlobals.SPToonfestTower3, self.base3)
        self.accept('enterbase1_collision', self.__handleOnBase1)
        self.accept('exitbase1_collision', self.__handleOffBase1)
        self.accept('enterbase2_collision', self.__handleOnBase2)
        self.accept('exitbase2_collision', self.__handleOffBase2)
        self.accept('enterbase3_collision', self.__handleOnBase3)
        self.accept('exitbase3_collision', self.__handleOffBase3)
        self.speedUpSound = base.loader.loadSfx('phase_6/audio/sfx/SZ_MM_gliss.ogg')
        self.changeDirectionSound = base.loader.loadSfx('phase_6/audio/sfx/SZ_MM_cymbal.ogg')
        self.__setupSpin()
        DistributedObject.DistributedObject.generate(self)

    def __setupSpin(self):
        taskMgr.add(self.__updateSpin, self.taskName('pianoSpinTask'))

    def __stopSpin(self):
        taskMgr.remove(self.taskName('pianoSpinTask'))

    def __updateSpin(self, task):
        now = globalClock.getFrameTime()
        if now > self.lerpFinish:
            offset = self.offset
        else:
            if now > self.lerpStart:
                t = (now - self.lerpStart) / (self.lerpFinish - self.lerpStart)
                offset = self.oldOffset + t * (self.offset - self.oldOffset)
            else:
                offset = self.oldOffset
        heading = self.degreesPerSecond * (now - self.spinStartTime) + offset
        self.base1.setHprScale(heading % 360.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.base2.setHprScale(heading % 360.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.base3.setHprScale(heading % 360.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        return Task.cont

    def disable(self):
        del self.base1
        del self.base2
        del self.base3
        base.cr.parentMgr.unregisterParent(ToontownGlobals.SPToonfestTower1)
        base.cr.parentMgr.unregisterParent(ToontownGlobals.SPToonfestTower2)
        base.cr.parentMgr.unregisterParent(ToontownGlobals.SPToonfestTower3)
        self.ignore('enterbase1_collision')
        self.ignore('exitbase1_collision')
        self.ignore('enterbase2_collision')
        self.ignore('exitbase2_collision')
        self.ignore('enterbase3_collision')
        self.ignore('exitbase3_collision')
        self.speedUpSound = None
        self.changeDirectionSound = None
        self.__stopSpin()
        DistributedObject.DistributedObject.disable(self)
        return

    def setSpeed(self, rpm, offset, timestamp):
        timestamp = globalClockDelta.networkToLocalTime(timestamp)
        degreesPerSecond = rpm / 60.0 * 360.0
        now = globalClock.getFrameTime()
        oldHeading = self.degreesPerSecond * (now - self.spinStartTime) + self.offset
        oldHeading = oldHeading % 360.0
        oldOffset = oldHeading - degreesPerSecond * (now - timestamp)
        self.rpm = rpm
        self.degreesPerSecond = degreesPerSecond
        self.offset = offset
        self.spinStartTime = timestamp
        while oldOffset - offset < -180.0:
            oldOffset += 360.0

        while oldOffset - offset > 180.0:
            oldOffset -= 360.0

        self.oldOffset = oldOffset
        self.lerpStart = now
        self.lerpFinish = timestamp + ChangeDirectionTime

    def playSpeedUp(self, avId):
        if avId != base.localAvatar.doId:
            pass

    def playChangeDirection(self, avId):
        if avId != base.localAvatar.doId:
            pass

    def __handleOnBase1(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('OnLayerOne')
        self.sendUpdate('requestSpeedUp', [])

    def __handleOffBase1(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('off')

    def __handleOnBase2(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('OnLayerTwo')
        self.sendUpdate('requestSpeedUp', [])

    def __handleOffBase2(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('off')

    def __handleOnBase3(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('OnLayerThree')
        self.sendUpdate('requestSpeedUp', [])

    def __handleOffBase3(self, collEntry):
        self.cr.playGame.getPlace().activityFsm.request('off')

    def __handleSpeedUpButton(self, collEntry):
        self.sendUpdate('requestSpeedUp', [])

    def __handleChangeDirectionButton(self, collEntry):
        now = globalClock.getFrameTime()
        if now - self.lastChangeDirection < ChangeDirectionDebounce:
            return
        self.lastChangeDirection = now
        self.sendUpdate('requestChangeDirection', [])