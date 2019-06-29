from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.battle import BattlePlace
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.toonbase import ToontownGlobals
from toontown.building import Elevator
from panda3d.core import *
from toontown.coghq import CogHQExterior
from toontown.safezone import GolfKart
from direct.distributed.ClockDelta import *
import random

class BossbotHQExterior(CogHQExterior.CogHQExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossbotHQExterior')
    GEAR_INDEX = xrange(12)
    GEYSER_INDEX = xrange(1, 5)

    def __init__(self, loader, parentFSM, doneEvent):
        CogHQExterior.CogHQExterior.__init__(self, loader, parentFSM, doneEvent)
        self.elevatorDoneEvent = 'elevatorDone'
        self.trains = None
        self.fsm.addState(State.State('elevator', self.enterElevator, self.exitElevator, ['walk', 'stopped', 'golfKartBlock']))
        self.fsm.addState(State.State('golfKartBlock', self.enterGolfKartBlock, self.exitGolfKartBlock, ['walk', 'stopped', 'elevator']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('elevator')
        state.addTransition('golfKartBlock')
        state = self.fsm.getStateNamed('stopped')
        state.addTransition('elevator')
        state.addTransition('golfKartBlock')
        state = self.fsm.getStateNamed('stickerBook')
        state.addTransition('elevator')
        state.addTransition('golfKartBlock')
        self.golfKartDoneEvent = 'golfKartDone'
        self.golfKartBlockDoneEvent = 'golfKartBlockDone'
        self.gearLerps = []
        return

    def enter(self, requestStatus):
        CogHQExterior.CogHQExterior.enter(self, requestStatus)
        self.loader.startCollisionDetection()
        self.loader.startBushCollisionDetection()

    def exit(self):
        CogHQExterior.CogHQExterior.exit(self)
        self.loader.stopCollisionDetection()
        self.loader.stopBushCollisionDetection()

    def enterElevator(self, distElevator, skipDFABoard=0):
        self.accept(self.elevatorDoneEvent, self.handleElevatorDone)
        self.elevator = Elevator.Elevator(self.fsm.getStateNamed('elevator'), self.elevatorDoneEvent, distElevator)
        if skipDFABoard:
            self.elevator.skipDFABoard = 1
        distElevator.elevatorFSM = self.elevator
        self.elevator.setReverseBoardingCamera(True)
        self.elevator.load()
        self.elevator.enter()

    def exitElevator(self):
        self.ignore(self.elevatorDoneEvent)
        self.elevator.unload()
        self.elevator.exit()
        del self.elevator

    def detectedElevatorCollision(self, distElevator):
        if self.fsm.getCurrentState().getName() == 'walk':
            self.fsm.request('elevator', [distElevator])

    def handleElevatorDone(self, doneStatus):
        self.notify.debug('handling elevator done event')
        where = doneStatus['where']
        if where == 'reject':
            if hasattr(base.localAvatar, 'elevatorNotifier') and base.localAvatar.elevatorNotifier.isNotifierOpen():
                pass
            else:
                self.fsm.request('walk')
        else:
            if where == 'exit':
                self.fsm.request('walk')
            else:
                if where == 'countryClubInterior':
                    self.doneStatus = doneStatus
                    messenger.send(self.doneEvent)
                else:
                    self.notify.error('Unknown mode: ' + where + ' in handleElevatorDone')

    def __handleOnFloor(self, collision):
        base.localAvatar.b_setParent(ToontownGlobals.SPDynamic + int(collision.getIntoNode().getName()[29:]))

    def __handleOffFloor(self, collision):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)

    def __cleanupDialog(self, value):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None
        if hasattr(self, 'fsm'):
            self.fsm.request('walk', [1])
        return

    def enterGolfKartBlock(self, golfKart):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        self.accept(self.golfKartDoneEvent, self.handleGolfKartDone)
        self.trolley = GolfKart.GolfKart(self, self.fsm, self.golfKartDoneEvent, golfKart.getDoId())
        self.trolley.load()
        self.trolley.enter()

    def exitGolfKartBlock(self):
        base.localAvatar.laffMeter.stop()
        self.trolley.unload()
        self.trolley.exit()
        del self.trolley

    def detectedGolfKartCollision(self, golfKart):
        self.notify.debug('detectedGolfkartCollision()')
        self.fsm.request('golfKartBlock', [golfKart])

    def handleStartingBlockDone(self, doneStatus):
        self.notify.debug('handling StartingBlock done event')
        where = doneStatus['where']
        if where == 'reject':
            self.fsm.request('walk')
        else:
            if where == 'exit':
                self.fsm.request('walk')
            else:
                if where == 'racetrack':
                    print 'Entering Racetrack'
                    self.doneStatus = doneStatus
                    messenger.send(self.doneEvent)
                else:
                    self.notify.error('Unknown mode: ' + where + ' in handleStartingBlockDone')

    def handleGolfKartDone(self, doneStatus):
        self.notify.debug('handling golf kart  done event')
        mode = doneStatus['mode']
        if mode == 'reject':
            self.fsm.request('walk')
        else:
            if mode == 'exit':
                self.fsm.request('walk')
            else:
                if mode == 'golfcourse':
                    self.doneStatus = {'loader': 'golfcourse', 'where': 'golfcourse', 'hoodId': self.loader.hood.id, 
                       'zoneId': doneStatus['zoneId'], 
                       'shardId': None, 
                       'courseId': doneStatus['courseId']}
                    messenger.send(self.doneEvent)
                else:
                    self.notify.error('Unknown mode: ' + mode + ' in handleGolfKartDone')
        return