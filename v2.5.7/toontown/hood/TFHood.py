from ToonHood import ToonHood
from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import ToontownGlobals
from toontown.safezone.TFSafeZoneLoader import TFSafeZoneLoader
from toontown.town.TFTownLoader import TFTownLoader
import SkyUtil
from direct.interval.IntervalGlobal import *
from toontown.toonfest.DayAndNightGlobals import *

class TFHood(ToonHood):
    notify = directNotify.newCategory('TFHood')

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ToontownGlobals.ToonFest
        self.townLoaderClass = TFTownLoader
        self.safeZoneLoaderClass = TFSafeZoneLoader
        self.storageDNAFile = 'phase_6/dna/storage_TF.jazz'
        self.skyFile = 'phase_3.5/models/props/TT_sky'
        self.spookySkyFile = 'phase_3.5/models/props/HW_2016_Sky'
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.sunriseTrack = None
        self.sunsetTrack = None
        self.FIX_TOD_DURATION = 1
        return

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('TFHood').addChild(self.fsm)

    def enter(self, *args):
        ToonHood.enter(self, *args)
        base.camLens.setNearFar(ToontownGlobals.SpeedwayCameraNear, ToontownGlobals.SpeedwayCameraFar)

    def exit(self):
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        ToonHood.exit(self)

    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)

    def setSunrise(self):
        self.sunriseTrack = Sequence(render.colorScaleInterval(SUNRISE_TIME, Vec4(0.29, 0.56, 1.0, 1)))
        if config.GetBool('toonfest-day-night', False):
            self.sunriseTrack.start()

    def setMorning(self):
        base.cr.playGame.hood.sky.setTransparency(1)
        SkyUtil.startCloudSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.sky.setScale(3)

    def setSunset(self):
        self.sunsetTrack = Sequence(render.colorScaleInterval(SUNSET_TIME, Vec4(0.22, 0.16, 0.76, 1)))
        if config.GetBool('toonfest-day-night', False):
            self.sunsetTrack.start()

    def setNight(self):
        pass

    def unload(self):
        self.parentFSM.getStateNamed('TFHood').removeChild(self.fsm)
        if self.sunriseTrack is not None:
            if self.sunriseTrack.isPlaying():
                self.sunriseTrack.finish()
        self.sunriseTrack = None
        del self.sunriseTrack
        if self.sunsetTrack is not None:
            if self.sunsetTrack.isPlaying():
                self.sunsetTrack.finish()
        self.sunsetTrack = None
        del self.sunsetTrack
        Sequence(render.colorScaleInterval(0, Vec4(1, 1, 1, 1))).start()
        ToonHood.unload(self)
        return

    def startSpookySky(self):
        if hasattr(self, 'sky') and self.sky:
            self.stopSky()
        self.sky = loader.loadModel(self.spookySkyFile)
        self.sky.setTag('sky', 'Halloween')
        self.sky.setScale(5.2)
        self.sky.setDepthTest(0)
        self.sky.setDepthWrite(0)
        self.sky.setColor(0.5, 0.5, 0.5, 1)
        self.sky.setBin('background', 100)
        self.sky.setFogOff()
        self.sky.reparentTo(camera)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        fadeIn = self.sky.colorScaleInterval(1.5, Vec4(1, 1, 1, 1), startColorScale=Vec4(1, 1, 1, 0.25), blendType='easeInOut')
        fadeIn.start()
        self.sky.setZ(0.0)
        self.sky.setHpr(0.0, 0.0, 0.0)
        ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
        self.sky.node().setEffect(ce)