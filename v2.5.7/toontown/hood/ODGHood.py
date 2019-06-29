from panda3d.core import *
import ToonHood
from toontown.town import ODGTownLoader
from toontown.safezone import ODGSafeZoneLoader
from toontown.toonbase.ToontownGlobals import *
import SkyUtil
from direct.interval.IntervalGlobal import *

class ODGHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = OldDaisyGardens
        self.townLoaderClass = ODGTownLoader.ODGTownLoader
        self.safeZoneLoaderClass = ODGSafeZoneLoader.ODGSafeZoneLoader
        self.storageDNAFile = 'phase_8/dna/storage_ODG.jazz'
        self.holidayStorageDNADict = {WINTER_DECORATIONS: None, WACKY_WINTER_DECORATIONS: None, 
           HALLOWEEN_PROPS: None, 
           SPOOKY_PROPS: None}
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.spookySkyFile = self.skyFile
        self.titleColor = (0.8, 0.6, 1.0, 1.0)
        self.laffMeter = base.localAvatar.laffMeter
        self.book = base.localAvatar.book.bookOpenButton
        self.book2 = base.localAvatar.book.bookCloseButton
        cm = CardMaker('card')
        cm.setFrameFullscreenQuad()
        self.explosionCard = render2d.attachNewNode(cm.generate())
        self.explosionCard.setTransparency(1)
        self.explosionCard.setColorScale(0, 0, 0, 0)
        return

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('ODGHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('ODGHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        pro2EvSeq = Sequence(Wait(3), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(localAvatar.sendUpdate, 'startPro2Ev', []))
        pro2SquirtEvSeq = Sequence(Func(NodePath(base.marginManager).hide), Func(self.explosionCard.setColorScale, 0, 0, 0, 1), Wait(3), Func(NodePath(self.book).hide), Func(NodePath(self.laffMeter).hide), Func(base.localAvatar.disableSleeping), Func(base.localAvatar.obscureFriendsListButton, 1), Func(base.localAvatar.hideClarabelleGui), Func(base.localAvatar.chatMgr.obscure, 1, 1), Func(localAvatar.sendUpdate, 'startPro2Ev', []), Wait(1), Func(self.explosionCard.setColorScale, 0, 0, 0, 0))
        if base.cr.currentEpisode == 'prologue':
            pro2EvSeq.start()
        else:
            if base.cr.currentEpisode == 'squirting_flower':
                pro2SquirtEvSeq.start()

    def exit(self):
        ToonHood.ToonHood.exit(self)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def startSky(self):
        if not self.sky.getTag('sky') == 'Regular':
            self.startSpookySky()
            return
        SkyUtil.startCloudSky(self)

    def startSpookySky(self):
        SkyUtil.startCloudSky(self)