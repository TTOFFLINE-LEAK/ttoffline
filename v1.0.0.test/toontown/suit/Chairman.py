from otp.avatar.Avatar import Avatar
from libotp import *
from toontown.toonbase import ToontownGlobals

class Chairman(Avatar):

    def __init__(self):
        Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.initializeNametag3d()
        self.initializeDropShadow()
        self.nametag3d.setPos(0, 0, 15.69)
        self.dropShadow.setScale(1.8)
        self.nametag3d.setScale(1.4)
        self.setPickable(0)
        self.loadModel('phase_14/models/char/chairman-mod')
        self.loadAnims({'neutral': 'phase_14/models/char/chairman-neutral'})
        self.setBlend(frameBlend=base.settings.getBool('game', 'smooth-animations', True))

    def getNametagJoints(self):
        return []