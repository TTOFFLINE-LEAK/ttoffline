import random
from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from otp.ai.MagicWordGlobal import *
from toontown.toonbase import ToontownGlobals

class DistributedPrologue3EventAI(DistributedObjectAI, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPrologu32EventAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'Prologue3EventFSM')
        self.air = air
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.toons = []
        self.suits = []

    def enterOff(self):
        self.requestDelete()

    def enterIdle(self):
        pass

    def enterEvent(self):
        event = simbase.air.doFind('Prologue3Event')
        if event is None:
            event = DistributedPrologue3EventAI(simbase.air)
            event.generateWithRequired(ToontownGlobals.OldOakStreet)
        taskMgr.doMethodLater(4, self.spawnCog, self.uniqueName('spawnCog'))
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

    def spawnCog(self, task):
        if self.air.currentEpisode != 'squirting_flower':
            return
        sp = simbase.air.suitPlanners.get(self.zoneId - self.zoneId % 100)
        if random.randint(0, 100) > 94:
            sp.createNewSuit([], sp.streetPointList, suitName='ms', suitLevel=5, specialSuit=0)
        else:
            sp.createNewSuit([], sp.streetPointList, suitName='gh', suitLevel=5, specialSuit=0)
        return task.done