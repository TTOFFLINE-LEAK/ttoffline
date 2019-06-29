import random
from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.actor import Actor
from direct.interval.IntervalGlobal import *
from toontown.battle import BattlePlace
from toontown.building import Elevator
from toontown.toonbase import ToontownGlobals
import FactoryExterior
DROP_POINTS = [(0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0),
 (0, -18, 1, 0, 0, 0)]

class CashbotHQShortChangeOffice(FactoryExterior.FactoryExterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotHQShortChangeOffice')

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
        self.chairNodeBase = None
        self.crossword = None
        self.crosswordDesc = None
        return

    def enterTeleportIn(self, requestStatus):
        dropPoint = random.choice(DROP_POINTS)
        base.localAvatar.setPosHpr(dropPoint[0], dropPoint[1], dropPoint[2], dropPoint[3], dropPoint[4], dropPoint[5])
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)

    def teleportInDone(self):
        BattlePlace.BattlePlace.teleportInDone(self)

    def shortCrash(self):
        propeller = Actor.Actor('phase_4/models/props/propeller-mod.bam', {'spin': 'phase_4/models/props/propeller-chan.bam'})
        propeller.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        propeller.reparentTo(hidden)
        startFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        crash = base.loader.loadSfx('phase_5/audio/sfx/TL_train_cog.ogg')
        land = base.loader.loadSfx('phase_5/audio/sfx/Toon_bodyfall_synergy.ogg')
        cogSuit = base.localAvatar.suit
        suit = base.localAvatar
        cogLeave = Sequence(ActorInterval(cogSuit, 'sit-lose'), Wait(0.1), Func(suit.setZ, 2.75), ActorInterval(cogSuit, 'landing', startTime=2.5, endTime=0), Wait(1.4), ActorInterval(cogSuit, 'slip-backward', playRate=0.75, startTime=0.3), Func(cogSuit.loop, 'neutral'))
        cogMovement = Sequence(Wait(3), Parallel(Sequence(suit.posInterval(0.5, (0,
                                                                                 15,
                                                                                 5)), suit.posInterval(1, (0,
                                                                                                           10,
                                                                                                           10)), suit.posInterval(0.7, (0,
                                                                                                                                        5,
                                                                                                                                        12)), Wait(0.05), suit.posInterval(0.55, (0,
                                                                                                                                                                                  0,
                                                                                                                                                                                  0), (0,
                                                                                                                                                                                       5,
                                                                                                                                                                                       9))), suit.hprInterval(1, (180,
                                                                                                                                                                                                                  0,
                                                                                                                                                                                                                  0))))
        spinTrack = Sequence(ActorInterval(propeller, 'spin', startTime=0, endTime=0.25))
        propellerTrack = Sequence(Wait(1), Func(propeller.reparentTo, suit.find('**/joint_head')), ActorInterval(propeller, 'spin', startTime=4, endTime=2), Func(spinTrack.loop), Wait(2.25), Func(spinTrack.finish), ActorInterval(propeller, 'spin'), Func(propeller.delete))
        soundTrack = Sequence(Wait(1), Parallel(SoundInterval(startFly, duration=5), Sequence(Wait(4.05), SoundInterval(crash)), Sequence(Wait(4.8), SoundInterval(land))))
        return Parallel(cogLeave, cogMovement, propellerTrack, soundTrack)

    def leaveCrossword(self):
        self.crossword.destroy()
        self.crosswordDesc.destroy()
        seq = Sequence(Func(self.shortCrash), Wait(1.3), Func(base.localAvatar.attachCamera), Func(base.localAvatar.initializeSmartCamera), Func(base.localAvatar.startUpdateSmartCamera), Wait(7.7), Func(base.localAvatar.collisionsOn), Func(base.localAvatar.enableAvatarControls)).start()

    def showCrossword(self):
        self.crossword = OnscreenImage(image='phase_14/maps/crossword.png', pos=(0,
                                                                                 0,
                                                                                 0), scale=(1,
                                                                                            1,
                                                                                            1))
        self.crossword.setTransparency(TransparencyAttrib.MAlpha)
        self.crossword.setColorScale(1, 1, 1, 1)
        self.crosswordDesc = OnscreenText(text='You have 60 seconds to solve the crossword!', pos=(0,
                                                                                                   0.3), scale=0.15, fg=(1,
                                                                                                                         1,
                                                                                                                         0.2,
                                                                                                                         1), shadow=(0,
                                                                                                                                     0,
                                                                                                                                     0,
                                                                                                                                     1), font=ToontownGlobals.getSuitFont(), align=TextNode.ACenter)
        self.crosswordDesc.reparentTo(render)

    def enterChair(self, collEntry):
        base.camera.wrtReparentTo(render)
        base.localAvatar.stopUpdateSmartCamera()
        base.localAvatar.shutdownSmartCamera()
        base.localAvatar.disableAvatarControls()
        base.localAvatar.collisionsOff()
        propeller = Actor.Actor('phase_4/models/props/propeller-mod.bam', {'spin': 'phase_4/models/props/propeller-chan.bam'})
        propeller.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        propeller.reparentTo(hidden)
        endFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        startFly = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        cogSuit = base.localAvatar.suit
        suit = base.localAvatar
        cogLeave = Sequence(Wait(0.1), ActorInterval(cogSuit, 'landing', startTime=2.5, endTime=0), ActorInterval(cogSuit, 'landing'), Func(suit.setZ, 1), Func(cogSuit.loop, 'sit'))
        cogMovement = Sequence(Wait(3), Parallel(Wait(1), suit.posInterval(1.5, (0,
                                                                                 15,
                                                                                 5))), suit.hprInterval(1, (0,
                                                                                                            0,
                                                                                                            0)))
        spinTrack = Sequence(ActorInterval(propeller, 'spin', startTime=0, endTime=0.25))
        propellerTrack = Sequence(Wait(1), Func(propeller.reparentTo, suit.find('**/joint_head')), ActorInterval(propeller, 'spin', startTime=4, endTime=2), Func(spinTrack.loop), Wait(2.25), Func(spinTrack.finish), ActorInterval(propeller, 'spin'), Func(propeller.delete))
        soundTrack = Sequence(Wait(1), Parallel(SoundInterval(startFly, duration=3), Sequence(Wait(2.5), SoundInterval(endFly))))
        crosswordTrack = Sequence(Wait(6.9), Func(self.showCrossword), Wait(60), Func(self.leaveCrossword))
        Parallel(cogLeave, cogMovement, propellerTrack, soundTrack, crosswordTrack).start()

    def setupCrossword(self):
        self.chairNodeBase = render.attachNewNode('chairNodeBase')
        self.chairNodeBase.setPos(-1.247, 17.806, 0.012)
        cs = CollisionSphere(0, 0, 0, 3)
        self.chairNode = self.chairNodeBase.attachNewNode(CollisionNode('chairNode'))
        self.chairNode.node().addSolid(cs)
        self.accept('enter' + self.chairNode.node().getName(), self.enterChair)

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