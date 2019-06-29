from panda3d.core import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
import FactoryInterior

class SwagtoryInterior(FactoryInterior.FactoryInterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('SwagtoryInterior')

    def __init__(self, loader, parentFSM, doneEvent):
        FactoryInterior.FactoryInterior.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        FactoryInterior.FactoryInterior.load(self)
        self.music = base.loader.loadMusic('phase_14.5/audio/bgm/CHQ_FACT_swing.ogg')

    def exit(self):
        localAvatar.setNametagScale(1.0)
        localAvatar.setCameraFov(ToontownGlobals.DefaultCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
        FactoryInterior.FactoryInterior.exit(self)