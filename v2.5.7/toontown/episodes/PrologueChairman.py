from otp.avatar.Avatar import Avatar
from otp.nametag.NametagGroup import NametagGroup
from toontown.toonbase import ToontownGlobals

class PrologueChairman(Avatar):

    def __init__(self):
        Avatar.__init__(self)
        self.setFont(ToontownGlobals.getSuitFont())
        self.setSpeechFont(ToontownGlobals.getSuitFont())
        self.setPlayerType(NametagGroup.CCSuit)
        self.initializeNametag3d()
        self.initializeDropShadow()
        self.nametag3d.setPos(0, 0, 15.69)
        self.dropShadow.setScale(1.8)
        self.nametag3d.setScale(1.4)
        self.setPickable(0)
        self.loadModel('phase_14/models/char/chairman-mod')
        self.loadAnims({'walk': 'phase_14/models/char/chairman-walk', 'neutral': 'phase_14/models/char/chairman-neutral', 
           'into-type': 'phase_14/models/char/chairman-into-type', 
           'type': 'phase_14/models/char/chairman-type', 
           'capture': 'phase_14/models/char/chairman-capture'})
        self.setBlend(frameBlend=config.GetBool('interpolate-animations', True))

    def getNametagJoints(self):
        return []