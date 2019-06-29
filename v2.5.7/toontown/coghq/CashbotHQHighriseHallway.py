import random
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.fsm import ClassicFSM
from direct.fsm import State
from toontown.battle import BattlePlace
from toontown.building import Elevator
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil
import FactoryExterior
DROP_POINTS = [(0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0),
 (0, 40, 0, -180, 0, 0)]

class CashbotHQHighriseHallway(FactoryExterior.FactoryExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotHQHighriseHallway')

    def __init__(self, loader, parentFSM, doneEvent):
        FactoryExterior.FactoryExterior.__init__(self, loader, parentFSM, doneEvent)
        self.elevatorDoneEvent = 'elevatorDone'
        self.trains = None
        self.fsm.addState(State.State('elevator', self.enterElevator, self.exitElevator, ['walk', 'stopped']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stopped')
        state.addTransition('elevator')
        state = self.fsm.getStateNamed('stickerBook')
        state.addTransition('elevator')
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        return

    def prepareFadeout(self):
        Seq = Sequence(Wait(3.5), Func(base.transitions.fadeOut), Wait(1), Func(self.bathroomTeleport), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Wait(3), Func(base.localAvatar.reparentTo, render), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                          0,
                                                                                                                                                                                                                                                          0)), Wait(1), Func(self.explosionCard.removeNode), Func(self.doors.removeNode))
        Seq.start()

    def bathroomTeleport(self):
        hoodId = ZoneUtil.getTrueZoneId(12000, 12000)
        zoneId = ZoneUtil.getTrueZoneId(12220, 12000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_12000_12220')
        tutorialFlag = 0
        requestStatus = {'loader': ZoneUtil.getLoaderName(zoneId), 'where': ZoneUtil.getToonWhereName(zoneId), 
           'how': how, 
           'hoodId': hoodId, 
           'zoneId': zoneId, 
           'shardId': None, 
           'tunnelOrigin': tunnelOriginPlaceHolder, 
           'tutorial': tutorialFlag, 
           'avId': -1}
        place = base.cr.playGame.getPlace()
        if place:
            place.requestLeave(requestStatus)
        return

    def swingDoors(self, door, side):
        if side == 'left':
            swingPos = [
             80, -60, 30]
        else:
            if side == 'right':
                swingPos = [
                 -80, 60, -30]
            else:
                raise ValueError('lol fuck you. here is an error. merry christmas.')
        openDoors = base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg')
        base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.wrtReparentTo(render.find('**/door_node'))
        self.cogReady = Sequence(Func(base.localAvatar.suit.loop, 'walk'), base.localAvatar.posHprInterval(0.5, (-6.9,
                                                                                                                 0,
                                                                                                                 0.0), (-90,
                                                                                                                        0,
                                                                                                                        0)), Func(base.localAvatar.suit.loop, 'neutral'))
        self.cogWalk = Sequence(Func(base.localAvatar.suit.loop, 'walk'), base.localAvatar.posInterval(2, (6.9,
                                                                                                           0,
                                                                                                           0.0)), Func(base.localAvatar.wrtReparentTo, render))
        self.cogEnter = Sequence(Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.collisionsOff), Parallel(Func(self.cogReady.start), base.camera.posHprInterval(1.69, (-5,
                                                                                                                                                                                                                                                                                  -20,
                                                                                                                                                                                                                                                                                  6), (-120,
                                                                                                                                                                                                                                                                                       -6.9,
                                                                                                                                                                                                                                                                                       0), blendType='easeInOut')), Func(self.prepareFadeout), Func(base.localAvatar.suit.loop, 'neutral'), Func(self.cogWalk.start))
        swingSequence = Sequence(Func(self.cogEnter.start), Wait(1.69), Func(base.playSfx, openDoors, volume=1), LerpHprInterval(door, 1, (swingPos[0], 0, 0), (0,
                                                                                                                                                                0,
                                                                                                                                                                0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (swingPos[1], 0, 0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (swingPos[2], 0, 0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (0,
                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                        0), blendType='easeInOut'))
        return swingSequence

    def handleDoorOpen(self, collEntry):
        self.ignore('enterdoor_collision')
        self.LSwing = self.swingDoors(self.Ldoor, 'left')
        self.RSwing = self.swingDoors(self.Rdoor, 'right')
        Parallel(self.LSwing, self.RSwing).start()

    def setupDoor(self):
        self.doors = loader.loadModel('phase_14/models/props/bathroom-doors')
        self.doors.reparentTo(render.find('**/door_node'))
        self.Ldoor = self.doors.find('**/L_door')
        self.Rdoor = self.doors.find('**/R_door')
        self.Ldoor.setY(4.1)
        self.Rdoor.setY(-4.1)
        self.accept('enterdoor_collision', self.handleDoorOpen)

    def enterTeleportIn(self, requestStatus):
        dropPoint = random.choice(DROP_POINTS)
        base.localAvatar.setPosHpr(dropPoint[0], dropPoint[1], dropPoint[2], dropPoint[3], dropPoint[4], dropPoint[5])
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)
        self.setupDoor()

    def teleportInDone(self):
        BattlePlace.BattlePlace.teleportInDone(self)

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
                if where == 'factoryExterior':
                    self.doneStatus = doneStatus
                    messenger.send(self.doneEvent)
                else:
                    self.notify.error('Unknown mode: ' + where + ' in handleElevatorDone')