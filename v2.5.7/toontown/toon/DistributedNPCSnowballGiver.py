from panda3d.core import *
from DistributedNPCToonBase import *
from toontown.quest import QuestParser
from toontown.quest import QuestChoiceGui
from toontown.quest import TrackChoiceGui
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
from toontown.toontowngui import TeaserPanel
from otp.nametag.NametagConstants import *

class DistributedNPCSnowballGiver(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)

    def delayDelete(self):
        DistributedNPCToonBase.delayDelete(self)
        DistributedNPCToonBase.disable(self)

    def handleCollisionSphereEnter(self, collEntry):
        sbCount = base.localAvatar.numPies
        if sbCount <= 0:
            self.sendUpdate('avatarEnter', [])

    def leave(self):
        self.removeActive()
        self.stash()

    def gaveSnowballs(self, npcId, avId, sbPhraseId):
        if not (base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_DECORATIONS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.WINTER_CAROLING)):
            self.ignoreAvatars()
            self.setChatAbsolute('Oh no! All of my snowballs melted! Oh well, see you next year!', CFSpeech | CFTimeout)
            self.animFSM.request('TeleportOut', [1, 0, self.leave, []])
            return
        if avId in base.cr.doId2do:
            avName = base.cr.doId2do.get(avId).getName()
            chatPhrases = [
             'A snowball a day, more and more Doodles will delay!',
             "Snowballs! Get your Snowballs! Straight from Loopy's Balls.",
             'Remember the technique! TECHNIQUE!',
             'Here you go %s, have some fun!' % avName]
            self.setChatAbsolute(chatPhrases[sbPhraseId], CFSpeech | CFTimeout)
        else:
            self.setChatAbsolute("Go get 'em!", CFSpeech | CFTimeout)