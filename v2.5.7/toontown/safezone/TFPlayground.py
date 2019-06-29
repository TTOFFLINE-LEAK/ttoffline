from panda3d.core import *
from direct.fsm import ClassicFSM, State
from direct.actor import Actor
from toontown.toonbase import ToontownGlobals
import PicnicBasket, Playground, random

class TFPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.fsm.addState(State.State('picnicBasketBlock', self.enterPicnicBasketBlock, self.exitPicnicBasketBlock, ['walk']))
        self.fsm.addState(State.State('activity', self.enterActivity, self.exitActivity, ['walk', 'stopped']))
        self.fsm.getStateNamed('walk').addTransition('picnicBasketBlock')
        self.fsm.getStateNamed('walk').addTransition('activity')
        self.activityFsm = ClassicFSM.ClassicFSM('Activity', [State.State('off', self.enterOff, self.exitOff, ['OnLayerOne', 'OnLayerTwo', 'OnLayerThree']),
         State.State('OnLayerOne', self.enterOnLayerOne, self.exitOnLayerOne, ['off', 'OnLayerTwo', 'OnLayerThree']),
         State.State('OnLayerTwo', self.enterOnLayerTwo, self.exitOnLayerTwo, ['off', 'OnLayerOne', 'OnLayerThree']),
         State.State('OnLayerThree', self.enterOnLayerThree, self.exitOnLayerThree, ['off', 'OnLayerOne', 'OnLayerTwo'])], 'off', 'off')
        self.activityFsm.enterInitialState()

    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        del self.activityFsm
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

    def exit(self):
        Playground.Playground.exit(self)

    def handleBookClose(self):
        Playground.Playground.handleBookClose(self)

    def teleportInDone(self):
        Playground.Playground.teleportInDone(self)

    def enterOff(self):
        return

    def exitOff(self):
        return

    def enterOnLayerOne(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPToonfestTower1)

    def exitOnLayerOne(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        base.localAvatar.setP(0)
        base.localAvatar.setR(0)

    def enterOnLayerTwo(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPToonfestTower2)

    def exitOnLayerTwo(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        base.localAvatar.setP(0)
        base.localAvatar.setR(0)

    def enterOnLayerThree(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPToonfestTower3)

    def exitOnLayerThree(self):
        base.localAvatar.b_setParent(ToontownGlobals.SPRender)
        base.localAvatar.setP(0)
        base.localAvatar.setR(0)

    def enterPicnicBasketBlock(self, picnicBasket):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.cantLeaveGame = 1
        self.accept('picnicBasketDone', self.handlePicnicBasketDone)
        self.trolley = PicnicBasket.PicnicBasket(self, self.fsm, 'picnicBasketDone', picnicBasket.getDoId(), picnicBasket.seatNumber)
        self.trolley.load()
        self.trolley.enter()

    def exitPicnicBasketBlock(self):
        base.localAvatar.laffMeter.stop()
        base.localAvatar.cantLeaveGame = 0
        self.ignore('picnicBasketDone')
        self.trolley.unload()
        self.trolley.exit()
        del self.trolley

    def enterActivity(self, setAnimState=True):
        if setAnimState:
            base.localAvatar.b_setAnimState('neutral', 1)
        self.accept('teleportQuery', self.handleTeleportQuery)
        base.localAvatar.setTeleportAvailable(False)
        base.localAvatar.laffMeter.start()

    def exitActivity(self):
        base.localAvatar.setTeleportAvailable(True)
        self.ignore('teleportQuery')
        base.localAvatar.laffMeter.stop()

    def detectedPicnicTableSphereCollision(self, picnicBasket):
        if self.fsm.getCurrentState().getName() == 'walk':
            self.fsm.request('picnicBasketBlock', [picnicBasket])

    def handlePicnicBasketDone(self, doneStatus):
        self.notify.debug('handling picnic basket done event')
        mode = doneStatus['mode']
        if mode == 'reject':
            self.fsm.request('walk')
        else:
            if mode == 'exit':
                self.fsm.request('walk')
            else:
                self.notify.error('Unknown mode: ' + mode + ' in handlePicnicBasketDone')