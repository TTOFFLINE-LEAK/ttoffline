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
DROP_POINTS = [(21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0),
 (21.43, 13.009, 0.025, 130.223, 0, 0)]

class CashbotHQBathroom(FactoryExterior.FactoryExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotHQBathroom')

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
        self.stallNodeBase = None
        self.doors = None
        return

    def prepareFadeout(self):
        Seq = Sequence(Wait(3.5), Func(base.transitions.fadeOut), Wait(1), Func(self.doors.removeNode), Func(self.bathroomTeleport), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Wait(3), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                            0,
                                                                                                                                                                                                                                            0)), Wait(1), Func(self.explosionCard.removeNode))
        Seq.start()

    def bathroomTeleport(self):
        self.stallNodeBase.removeNode()
        hoodId = ZoneUtil.getTrueZoneId(12000, 12000)
        zoneId = ZoneUtil.getTrueZoneId(12210, 12000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_12000_12210')
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

    def SwingDoors(self, door, side):
        if side == 'left':
            swingPos = [
             80, -60, 30]
        else:
            if side == 'right':
                swingPos = [
                 -80, 60, -30]
            else:
                print 'lol fuck you. here is an error. merry christmas.'
        openDoors = base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg')
        base.localAvatar.b_setAnimState('neutral')
        base.localAvatar.wrtReparentTo(render.find('**/uniqueDoorNode'))
        self.cogReady = Sequence(Func(base.localAvatar.suit.loop, 'walk'), base.localAvatar.posHprInterval(0.5, (-6.9,
                                                                                                                 0,
                                                                                                                 0.0), (-90,
                                                                                                                        0,
                                                                                                                        0)), Func(base.localAvatar.suit.loop, 'neutral'))
        self.cogWalk = Sequence(Func(base.localAvatar.suit.loop, 'walk'), base.localAvatar.posInterval(2, (8,
                                                                                                           0,
                                                                                                           0.0)), Func(base.localAvatar.wrtReparentTo, render))
        self.cogEnter = Sequence(Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.disableAvatarControls), Func(base.localAvatar.collisionsOff), Parallel(Func(self.cogReady.start), base.camera.posHprInterval(1.69, (11.097,
                                                                                                                                                                                                                                                                                  6.687,
                                                                                                                                                                                                                                                                                  9.9445), (-57.0,
                                                                                                                                                                                                                                                                                            -10.0,
                                                                                                                                                                                                                                                                                            0.0), blendType='easeInOut')), Func(self.prepareFadeout), Func(base.localAvatar.suit.loop, 'neutral'), Func(self.cogWalk.start))
        SwingSequence = Sequence(Func(self.cogEnter.start), Wait(1.69), Func(base.playSfx, openDoors, volume=1), LerpHprInterval(door, 1, (swingPos[0], 0, 0), (0,
                                                                                                                                                                0,
                                                                                                                                                                0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (swingPos[1], 0, 0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (swingPos[2], 0, 0), blendType='easeInOut'), LerpHprInterval(door, 1.5, (0,
                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                        0), blendType='easeInOut'))
        return SwingSequence

    def handleDoorOpen(self, collEntry):
        self.ignore('enterdoor_collision')
        self.LSwing = self.SwingDoors(self.Ldoor, 'left')
        self.RSwing = self.SwingDoors(self.Rdoor, 'right')
        Parallel(self.LSwing, self.RSwing).start()

    def setupDoor(self):
        self.doors = loader.loadModel('phase_14/models/props/bathroom-doors.bam')
        self.doors.reparentTo(render)
        self.doors.setPosHpr(35.666, 22.974, 0.0, 47.6, 0.0, 0.0)
        self.uniqueDoorNode = self.doors.attachNewNode('uniqueDoorNode')
        self.doorBox = CollisionBox(0, 0.69, 4, 1)
        self.doorBoxNode = CollisionNode('doorNode')
        self.doorBoxNode.addSolid(self.doorBox)
        self.doorBoxNodePath = self.uniqueDoorNode.attachNewNode(self.doorBoxNode)
        self.Ldoor = self.doors.find('**/L_door')
        self.Rdoor = self.doors.find('**/R_door')
        self.Ldoor.setY(4.1042)
        self.Rdoor.setY(-4.1042)
        self.accept('enterdoorNode', self.handleDoorOpen)

    def enterStall(self, collEntry):
        pissSfx = base.loader.loadSfx('phase_5/audio/sfx/AA_squirt_seltzer.ogg')
        self.ignore('enter' + self.stallNode.node().getName())
        seq = Sequence(self.explosionCard.colorScaleInterval(1, (0, 0, 0, 1)), Wait(1), Func(base.playSfx, pissSfx, volume=1), Wait(1), Func(base.playSfx, pissSfx, volume=1), Wait(1), Func(base.localAvatar.setPosHpr, 34.045, -1.995, 0.025, 269, 0, 0), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                                      0)), Func(base.localAvatar.displayTalk, 'What a relaxing oil cleaning that was.')).start()

    def setupStall(self):
        self.stallNodeBase = render.attachNewNode('stallNodeBase')
        self.stallNodeBase.setPos(-9.857, -36.127, 1.116)
        cs = CollisionSphere(0, 0, 0, 2)
        self.stallNode = self.stallNodeBase.attachNewNode(CollisionNode('stallNode'))
        self.stallNode.node().addSolid(cs)
        self.accept('enter' + self.stallNode.node().getName(), self.enterStall)

    def enterTeleportIn(self, requestStatus):
        dropPoint = random.choice(DROP_POINTS)
        base.localAvatar.setPosHpr(dropPoint[0], dropPoint[1], dropPoint[2], dropPoint[3], dropPoint[4], dropPoint[5])
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)
        self.setupDoor()
        self.setupStall()

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