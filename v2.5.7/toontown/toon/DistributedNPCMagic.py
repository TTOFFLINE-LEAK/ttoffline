from panda3d.core import *
from DistributedNPCToonBase import *
from direct.gui.DirectGui import *
from panda3d.core import *
import NPCToons
from toontown.toonbase import TTLocalizer
from direct.distributed import DistributedObject
from toontown.quest import QuestParser
from otp.nametag.NametagConstants import *

class DistributedNPCMagic(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.movie = None
        return

    def delete(self):
        if self.movie:
            self.movie.finish()
        DistributedNPCToonBase.delete(self)

    def initToonState(self):
        self.setAnimState('neutral', 1.0, None, None)
        self.setPos(-162.724, -40.578, 0.025)
        self.setH(-37)
        return

    def handleCollisionSphereEnter(self, collEntry):
        self.sendUpdate('avatarEnter', [])

    def doSequence(self, avId):
        avName = base.cr.doId2do.get(avId).getName()
        self.clearChat()
        fullString = "Oh, hiya there Toon! Hey, wanna see something cool?\x07I'm getting bigger, and bigger, and bigger! And- 2\x07Nooooooooooo!"
        self.acceptOnce('doneChatPage', self.playNextEvent)
        self.setLocalPageChat(fullString, 1)

    def playNextEvent(self, number):
        print 'playNextEvent number: %s' % number