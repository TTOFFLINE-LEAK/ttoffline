from panda3d.core import *
from direct.interval.IntervalGlobal import *
import ToonHood
from toontown.town import SBTownLoader
from toontown.safezone import SBSafeZoneLoader
from toontown.toonbase.ToontownGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toon import NPCToons
from direct.gui.OnscreenText import OnscreenText
from toontown.hood import ZoneUtil
import SkyUtil

class SBHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ScroogeBank
        self.townLoaderClass = SBTownLoader.SBTownLoader
        self.safeZoneLoaderClass = SBSafeZoneLoader.SBSafeZoneLoader
        self.storageDNAFile = 'phase_8/dna/storage_ODG.jazz'
        self.holidayStorageDNADict = {WINTER_DECORATIONS: ['phase_8/dna/winter_storage_SB.jazz'], WACKY_WINTER_DECORATIONS: [
                                    'phase_8/dna/winter_storage_SB.jazz'], 
           HALLOWEEN_PROPS: None, 
           SPOOKY_PROPS: None}
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.spookySkyFile = self.skyFile
        self.titleColor = (0.8, 0.6, 1.0, 1.0)
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        self.warning = OnscreenText(text='You need a key to enter.', pos=(0, -0.6), scale=0.1, font=ToontownGlobals.getSignFont(), fg=(1,
                                                                                                                                       1,
                                                                                                                                       1,
                                                                                                                                       1), shadow=(0.1,
                                                                                                                                                   0.1,
                                                                                                                                                   0.1,
                                                                                                                                                   1))
        self.warning.setColorScale(1, 1, 1, 0)
        self.warningInterval = Sequence(self.warning.colorScaleInterval(1.969, (1,
                                                                                1,
                                                                                1,
                                                                                1)), Wait(1.5), self.warning.colorScaleInterval(2, (1,
                                                                                                                                    1,
                                                                                                                                    1,
                                                                                                                                    0)))
        self.enterSfx = loader.loadSfx('phase_3/audio/sfx/tt_s_ara_mat_crash_woodGlass.ogg')
        self.col = loader.loadModel('phase_9/models/cogHQ/CogDoor_Button')
        self.col.setPosHpr(-19.69, 0, 25.385, 90, -90, 0)
        self.col.setScale(3)
        self.col.reparentTo(render)
        self.colNode = None
        return

    def teleportToBankInterior(self):
        hoodId = ZoneUtil.getTrueZoneId(21000, 21000)
        zoneId = ZoneUtil.getTrueZoneId(21401, 21000)
        how = 'teleportIn'
        tunnelOriginPlaceHolder = render.attachNewNode('toph_21000_21401')
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

    def startCollDetect(self):
        if not self.colNode:
            cs = CollisionSphere(0, 0, 0, 2)
            self.colNode = self.col.attachNewNode(CollisionNode('cnode4'))
            self.colNode.node().addSolid(cs)
        self.accept('enter' + self.colNode.node().getName(), self.handleCollision)

    def stopCollDetect(self):
        if self.colNode:
            self.ignore('enter' + self.colNode.node().getName())

    def handleCollision(self, collEntry):
        self.walkin = Sequence(Func(base.playSfx, self.enterSfx, volume=1), self.col.colorScaleInterval(1, (0,
                                                                                                            1,
                                                                                                            0,
                                                                                                            1)), Wait(1), Func(self.teleportToBankInterior), Func(NodePath(self.laffMeter).hide), Func(base.camera.wrtReparentTo, render), Func(base.localAvatar.stopUpdateSmartCamera), Func(base.localAvatar.shutdownSmartCamera), Func(base.camera.setPosHpr, -190.877, 0, 30, 270, 12, 0), base.camera.posHprInterval(2.69, (-50.877,
                                                                                                                                                                                                                                                                                                                                                                                                                                 0,
                                                                                                                                                                                                                                                                                                                                                                                                                                 119), (270,
                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                        0), blendType='easeInOut'))
        self.stopforasec = Sequence(Func(self.stopCollDetect), Wait(6), Func(self.startCollDetect))
        if base.cr.scroogeKey == 0:
            self.warningInterval.start()
            self.stopforasec.start()
        else:
            self.stopCollDetect()
            base.cr.scroogeKey = 2
            self.walkin.start()

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('SBHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('SBHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        localAvatar.setCameraFov(CogHQCameraFov)
        base.camLens.setNearFar(CogHQCameraNear, CogHQCameraFar)
        proEvSeq = Sequence(Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Wait(3), Func(localAvatar.sendUpdate, 'startProEv', []), Func(self.startCollDetect), self.explosionCard.colorScaleInterval(2, (0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                        0)))
        proEvSeq.start()

    def exit(self):
        localAvatar.setCameraFov(DefaultCameraFov)
        base.camLens.setNearFar(DefaultCameraNear, DefaultCameraFar)
        ToonHood.ToonHood.exit(self)
        base.localAvatar.attachCamera()
        base.localAvatar.initializeSmartCamera()
        base.localAvatar.startUpdateSmartCamera()
        self.stopCollDetect()
        self.col.removeNode()
        del self.col

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        if not self.sky.getTag('sky') == 'Regular':
            self.startSpookySky()
            return
        SkyUtil.startCloudSky(self)

    def startSpookySky(self):
        SkyUtil.startCloudSky(self)