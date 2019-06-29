from otp.ai.AIBase import *
from toontown.toonbase import ToontownGlobals
from direct.distributed.ClockDelta import *
from toontown.building import ElevatorConstants
from toontown.building import DistributedElevatorExtAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
import CogDisguiseGlobals

class DummyBldg:

    def getDoId(self):
        return 0


class DistributedShortChangeElevatorAI(DistributedElevatorExtAI.DistributedElevatorExtAI):

    def __init__(self, air, index, x, y, z, h, p, r, minLaff):
        self.posHpr = (
         x, y, z, h, p, r)
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, DummyBldg(), minLaff=minLaff)
        self.type = ElevatorConstants.ELEVATOR_NORMAL
        self.countdownTime = ElevatorConstants.ElevatorData[self.type]['countdown']
        self.index = index

    def getPosHpr(self):
        return self.posHpr

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            players = []
            for i in self.seats:
                if i not in (None, 0):
                    players.append(i)

            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setDestinationZone', [ToontownGlobals.CashbotHighriseHallway])
                    self.clearFullNow(seatIndex)

        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')
        return

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def sendAvatarsToDestination(self, avIdList):
        if len(avIdList) > 0:
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setDestinationZoneForce', [ToontownGlobals.CashbotHighriseHallway])