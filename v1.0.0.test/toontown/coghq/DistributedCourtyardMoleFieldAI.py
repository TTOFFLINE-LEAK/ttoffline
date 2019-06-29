from toontown.coghq import MoleFieldBase
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
from toontown.toonbase import ToontownGlobals

class DistributedCourtyardMoleFieldAI(DistributedObjectAI.DistributedObjectAI, MoleFieldBase.MoleFieldBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMoleFieldAI')
    RebootTaskName = 'rebootMolesTask'

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.whackedMoles = {}
        self.started = 0
        self.numMoles = len(ToontownGlobals.MoleHillPositions)
        self.entId = 1

    def delete(self):
        DistributedObjectAI.DistributedObjectAI.delete(self)
        self.removeAllTasks()

    def b_setGameStart(self, timestamp):
        self.d_setGameStart(timestamp)
        self.setGameStart(timestamp)

    def d_setGameStart(self, timestamp):
        self.notify.debug('BASE: Sending setGameStart')
        self.sendUpdate('setGameStart', [timestamp])

    def setGameStart(self, timestamp):
        self.notify.debug('BASE: setGameStart')
        self.prepareForGameStartOrRestart()

    def prepareForGameStartOrRestart(self):
        self.scheduleMoles()
        self.whackedMoles = {}

    def whackedMole(self, moleIndex, popupNum):
        validMoleWhack = False
        if moleIndex in self.whackedMoles:
            if self.whackedMoles[moleIndex] < popupNum:
                validMoleWhack = True
        else:
            self.whackedMoles[moleIndex] = popupNum
            validMoleWhack = True
        if validMoleWhack:
            self.sendUpdate('updateMole', [moleIndex, self.WHACKED])

    def whackedBomb(self, moleIndex, popupNum, timestamp):
        senderId = self.air.getAvatarIdFromSender()
        self.sendUpdate('reportToonHitByBomb', [senderId, moleIndex, timestamp])

    def restartGame(self, task=None):
        self.gameStartTime = globalClock.getRealTime()
        self.started = 0
        self.b_setGameStart(globalClockDelta.localToNetworkTime(self.gameStartTime))
        taskMgr.doMethodLater(900, self.restartGame, self.RebootTaskName)