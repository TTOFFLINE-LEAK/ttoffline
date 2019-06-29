from direct.fsm import State
from toontown.safezone import PicnicBasket
import Playground

class SPPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.parentFSM = parentFSM
        self.picnicBasketBlockDoneEvent = 'picnicBasketBlockDone'
        self.fsm.addState(State.State('picnicBasketBlock', self.enterPicnicBasketBlock, self.exitPicnicBasketBlock, ['walk']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('picnicBasketBlock')
        self.picnicBasketDoneEvent = 'picnicBasketDone'

    def createPicnic(self, picnicBasket):
        self.accept(self.picnicBasketDoneEvent, self.handlePicnicBasketDone)
        place = base.cr.playGame.getPlace()
        if not hasattr(place, 'picnic') or not place.picnic:
            place.picnic = PicnicBasket.PicnicBasket(place, place.fsm, self.picnicBasketDoneEvent, picnicBasket.getDoId(), picnicBasket.seatNumber)
            place.picnic.load()
            place.picnic.enter()

    def enterPicnicBasketBlock(self, picnicBasket):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.cantLeaveGame = 1
        self.createPicnic(picnicBasket)

    def exitPicnicBasketBlock(self):
        base.localAvatar.laffMeter.stop()
        base.localAvatar.cantLeaveGame = 0
        self.ignore(self.picnicBasketDoneEvent)
        place = base.cr.playGame.getPlace()
        if hasattr(place, 'picnic') and place.picnic:
            place.picnic.unload()
            place.picnic.exit()
        place.picnic = None
        return

    def detectedPicnicTableSphereCollision(self, picnicBasket):
        if self.fsm.getCurrentState().getName() != 'picnicBasketBlock':
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