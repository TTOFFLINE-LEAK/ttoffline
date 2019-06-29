from direct.distributed.ClockDelta import *
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from otp.ai.MagicWordGlobal import *

class DistributedPrologue4EventAI(DistributedObjectAI, FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPrologue4EventAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        FSM.__init__(self, 'Prologue4EventFSM')
        self.air = air
        self.stateTime = globalClockDelta.getRealNetworkTime()
        self.toons = []
        self.suits = []

    def enterOff(self):
        self.requestDelete()

    def enterIdle(self):
        pass

    def enterEvent(self):
        event = simbase.air.doFind('Prologue4Event')
        if event is None:
            event = DistributedPrologue4EventAI(simbase.air)
            event.generateWithRequired(21834)
        taskMgr.doMethodLater(400, self.b_setState, self.uniqueName('EventTwo'), extraArgs=['EventTwo'])
        self.showAnnounceInterval = Sequence(Wait(14), Func(self.sendGlobalUpdate, 'TOON HQ: The Toon Council Presidential Elections will be starting any second!'), Wait(5), Func(self.sendGlobalUpdate, 'TOON HQ: Please silence your Shtickerbooks and keep any Oinks, Squeaks, and Owooos to a low rustle.'))
        if self.air.inEpisode and self.air.currentEpisode == 'prologue':
            self.showAnnounceInterval.start()
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

    def sendGlobalUpdate(self, text):
        for doId in simbase.air.doId2do:
            if str(doId)[:2] == '10':
                do = simbase.air.doId2do.get(doId)
                do.d_setSystemMessage(0, text)