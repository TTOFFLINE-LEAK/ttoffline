from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from otp.ai.MagicWordGlobal import *

class DistributedSquirtingFlowerEventAI(DistributedObjectAI, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSquirtingFlowerEventAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'SquirtingFlowerEventFSM')
        self.air = air
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.toons = []
        self.suits = []

    def enterOff(self):
        self.requestDelete()

    def enterIdle(self):
        pass

    def enterEvent(self):
        event = simbase.air.doFind('SquirtingFlowerEvent')
        if event is None:
            event = DistributedSquirtingFlowerEventAI(simbase.air)
            event.generateWithRequired('21821')
        taskMgr.doMethodLater(82, self.b_setState, self.uniqueName('EventTwo'), extraArgs=['EventTwo'])
        return

    def enterEventTwo(self):
        pass

    def setState(self, state):
        self.demand(state)

    def d_setState(self, state):
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTime])

    def b_setState(self, state):
        self.setState(state)
        self.d_setState(state)

    def getState(self):
        return (
         self.state, self.stateTime)