from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObject import DistributedObject
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from panda3d.core import *

class DistributedSquirtingFlowerEvent(DistributedObject, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSquirtingFlowerEvent')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, 'SquirtingFlowerEventFSM')
        self.cr.squirtingflowerEvent = self
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        base.localAvatar.attachCamera()
        base.localAvatar.initializeSmartCamera()
        base.localAvatar.startUpdateSmartCamera()

    def enterOff(self, offset):
        pass

    def exitOff(self):
        pass

    def __cleanupNPCs(self):
        pass

    def delete(self):
        self.demand('Off', 0.0)
        self.ignore('entercnode')
        self.newsky.removeNode()
        del self.newsky
        self.__cleanupNPCs()
        DistributedObject.delete(self)

    def resetCameraFollow(self):
        pass

    def enterIdle(self, offset):
        pass

    def exitIdle(self):
        pass

    def enterEvent(self, offset):
        self.coachTalk = Sequence(Wait(5), Func(base.localAvatar.displayTalk, 'Boy, what a workout!'))
        self.coachTalk.start()
        self.coachTalk.setT(offset)

    def exitEvent(self):
        self.coachTalk.finish()

    def enterEventTwo(self, offset):
        pass

    def exitEventTwo(self):
        pass

    def setState(self, state, timestamp):
        self.request(state, globalClockDelta.localElapsedTime(timestamp))