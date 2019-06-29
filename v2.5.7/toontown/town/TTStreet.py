from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
import Street

class TTStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        self.title = OnscreenText(text='Chapter One - Operations Collide', pos=(0,
                                                                                -0.6), scale=0.169, font=ToontownGlobals.getSuitFont(), fg=(1,
                                                                                                                                            1,
                                                                                                                                            1,
                                                                                                                                            1), shadow=(0.1,
                                                                                                                                                        0.1,
                                                                                                                                                        0.1,
                                                                                                                                                        1))
        self.title.setColorScale(1, 1, 1, 0)
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        base.localAvatar.cameraFollow = 1

    def resetCameraFollow(self):
        base.localAvatar.cameraFollow = 0

    def load(self):
        Street.Street.load(self)
        if hasattr(base.cr, 'inEvToonHall') and base.cr.inEvToonHall:
            sillyMeterSign = self.loader.geom.find('**/sillyOMeterSign')
            if sillyMeterSign:
                sillyMeterSign.removeNode()
            self.cinematicTitle = Sequence(self.title.colorScaleInterval(1.969, (1,
                                                                                 1,
                                                                                 1,
                                                                                 1)), Wait(4.5), self.title.colorScaleInterval(2, (1,
                                                                                                                                   1,
                                                                                                                                   1,
                                                                                                                                   0)))
            evToonHallSeq = Sequence(Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Func(base.localAvatar.disableAvatarControls), Func(NodePath(self.laffMeter).hide), Func(NodePath(base.marginManager).hide), Func(base.localAvatar.disableSleeping), Func(NodePath(self.book).hide), Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.camera.setPosHpr, 24, -26, 6, 45, 0, 0), Wait(2), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      0)), Wait(1), Func(self.cinematicTitle.start), Func(self.resetCameraFollow))
            evToonHallSeq.start()
        if hasattr(base.cr, 'inEvAftermathToonHall') and base.cr.inEvAftermathToonHall:
            sillyMeterSign = self.loader.geom.find('**/sillyOMeterSign')
            if sillyMeterSign:
                sillyMeterSign.removeNode()

    def unload(self):
        Street.Street.unload(self)

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])