from direct.directnotify import DirectNotifyGlobal
from toontown.safezone import DistributedGolfKartAI
from toontown.building import DistributedElevatorExtAI
from toontown.building import DistributedElevatorAI
from toontown.building import ElevatorConstants
from toontown.toonbase import ToontownGlobals

class DummyBldg:

    def getDoId(self):
        return 0


class DistributedSwagKartAI(DistributedElevatorExtAI.DistributedElevatorExtAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSwagKartAI')

    def __init__(self, air, index, x, y, z, h, p, r, minLaff):
        self.posHpr = (
         x, y, z, h, p, r)
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, DummyBldg(), minLaff=minLaff)
        self.type = ElevatorConstants.ELEVATOR_WEST_WING
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
                    self.sendUpdateToAvatarId(avId, 'setDestinationZone', [ToontownGlobals.SellbotWestWing])
                    self.clearFullNow(seatIndex)

        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')
        return

    def sendAvatarsToDestination(self, avIdList):
        if len(avIdList) > 0:
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setDestinationZoneForce', [ToontownGlobals.SellbotWestWing])

    def enterClosing(self):
        DistributedElevatorAI.DistributedElevatorAI.enterClosing(self)
        taskMgr.doMethodLater(ElevatorConstants.ElevatorData[ElevatorConstants.ELEVATOR_WEST_WING]['closeTime'], self.elevatorClosedTask, self.uniqueName('closing-timer'))

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')