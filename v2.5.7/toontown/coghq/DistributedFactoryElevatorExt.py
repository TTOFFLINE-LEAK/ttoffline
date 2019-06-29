from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import *
from toontown.building import DistributedElevatorExt
from toontown.building import DistributedElevator
from toontown.toonbase import ToontownGlobals
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.hood import ZoneUtil
from toontown.toonbase import TTLocalizer

class DistributedFactoryElevatorExt(DistributedElevatorExt.DistributedElevatorExt):

    def __init__(self, cr):
        DistributedElevatorExt.DistributedElevatorExt.__init__(self, cr)
        self.isSwagtory = False
        if self.zoneId == ToontownGlobals.SellbotWestWing:
            self.type = ELEVATOR_WEST_WING_THICC

    def generate(self):
        DistributedElevatorExt.DistributedElevatorExt.generate(self)

    def delete(self):
        self.elevatorModel.removeNode()
        del self.elevatorModel
        DistributedElevatorExt.DistributedElevatorExt.delete(self)

    def setEntranceId(self, entranceId):
        self.entranceId = entranceId
        if self.entranceId == 0:
            self.elevatorModel.setPosHpr(62.74, -85.31, 0.0, 2.0, 0.0, 0.0)
        else:
            if self.entranceId == 1:
                self.elevatorModel.setPosHpr(-162.25, 26.43, 0.0, 269.0, 0.0, 0.0)
            else:
                if self.entranceId == 2:
                    self.elevatorModel.setPosHpr(7.41, 195.56, 0.96, 358.15, 0.0, 0.0)
                else:
                    self.notify.error('Invalid entranceId: %s' % entranceId)

    def setupElevator(self):
        if self.zoneId == ToontownGlobals.SellbotWestWing:
            self.elevatorModel = loader.loadModel('phase_14/models/modules/thicc-elevator')
            self.leftDoor = self.elevatorModel.find('**/left_door')
            self.rightDoor = self.elevatorModel.find('**/right_door')
        else:
            self.elevatorModel = loader.loadModel('phase_4/models/modules/elevator')
            self.elevatorModel.find('**/light_panel').removeNode()
            self.elevatorModel.find('**/light_panel_frame').removeNode()
            self.leftDoor = self.elevatorModel.find('**/left-door')
            self.rightDoor = self.elevatorModel.find('**/right-door')
        self.elevatorModel.reparentTo(render)
        self.elevatorModel.setScale(1.05)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getElevatorModel(self):
        return self.elevatorModel

    def setBldgDoId(self, bldgDoId):
        self.bldg = None
        self.setupElevator()
        return

    def getZoneId(self):
        return 0

    def __doorsClosed(self, zoneId):
        pass

    def setFactoryInteriorZone(self, zoneId):
        if self.localToonOnBoard:
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader', 'where': 'factoryInterior', 
               'how': 'teleportIn', 
               'zoneId': zoneId, 
               'hoodId': hoodId}
            if self.isSwagtory:
                doneStatus['where'] = 'swagtoryInterior'
            self.cr.playGame.getPlace().elevator.signalDone(doneStatus)

    def setSwagtory(self, isSwagtory):
        self.isSwagtory = isSwagtory

    def setFactoryInteriorZoneForce(self, zoneId):
        place = self.cr.playGame.getPlace()
        if place:
            place.fsm.request('elevator', [self, 1])
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader', 'where': 'factoryInterior', 
               'how': 'teleportIn', 
               'zoneId': zoneId, 
               'hoodId': hoodId}
            if hasattr(place, 'elevator') and place.elevator:
                place.elevator.signalDone(doneStatus)
            else:
                self.notify.warning("setMintInteriorZoneForce: Couldn't find playGame.getPlace().elevator, zoneId: %s" % zoneId)
        else:
            self.notify.warning("setFactoryInteriorZoneForce: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def getDestName(self):
        if self.entranceId == 0:
            return TTLocalizer.ElevatorSellBotFactory0
        if self.entranceId == 1:
            return TTLocalizer.ElevatorSellBotFactory1
        if self.entranceId == 2:
            return TTLocalizer.ElevatorSellBotFactory2