from otp.ai.AIBase import *
from toontown.toonbase import ToontownGlobals
from direct.distributed.ClockDelta import *
from toontown.building.ElevatorConstants import *
from toontown.building import DistributedElevatorExtAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
import random

class DistributedFactoryElevatorExtAI(DistributedElevatorExtAI.DistributedElevatorExtAI):

    def __init__(self, air, bldg, factoryId, entranceId, antiShuffle=0, minLaff=0, isSwagtory=False):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, bldg, antiShuffle=antiShuffle, minLaff=minLaff)
        self.factoryId = factoryId
        self.entranceId = entranceId
        self.isSwagtory = isSwagtory

    def getEntranceId(self):
        return self.entranceId

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            players = []
            for i in self.seats:
                if i not in (None, 0):
                    players.append(i)

            if self.isSwagtory:
                factoryZone = self.bldg.createFactory(ToontownGlobals.SwagFactoryInt, 0, players)
            else:
                factoryZone = self.bldg.createFactory(self.factoryId, self.entranceId, players)
            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setSwagtory', [self.isSwagtory])
                    self.sendUpdateToAvatarId(avId, 'setFactoryInteriorZone', [factoryZone])
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
            factoryZone = self.bldg.createFactory(self.factoryId, self.entranceId, avIdList)
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setFactoryInteriorZoneForce', [factoryZone])